"""
Extractor de datos de facturas para LACTALIS COMPRAS
"""

import xml.etree.ElementTree as ET
import logging
import re
from typing import Dict, List

from config.constants import NAMESPACES, CURRENCY_CODE_MAP

logger = logging.getLogger(__name__)


class FacturaExtractorLactalis:
    """Extractor de datos de facturas para LACTALIS COMPRAS"""

    def __init__(self, xml_content: str):
        # Limpiar el XML de namespaces si es necesario
        self.xml_content = self._clean_xml(xml_content)
        self.root = ET.fromstring(self.xml_content)
        self.ns = NAMESPACES

    def _clean_xml(self, xml_content: str) -> str:
        """Limpia el XML de CDATA y namespaces conflictivos"""
        # Extraer de CDATA si existe
        cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', xml_content, re.DOTALL)
        if cdata_match:
            xml_content = cdata_match.group(1)

        return xml_content

    def _get_text(self, xpath: str, default: str = "", element=None) -> str:
        """Extrae texto de un elemento XML"""
        if element is None:
            element = self.root

        # Intentar con namespaces
        elem = element.find(xpath, self.ns)
        if elem is not None and elem.text:
            return elem.text.strip()

        # Intentar sin namespaces
        simple_xpath = xpath.replace('cac:', '').replace('cbc:', '').replace('ext:', '').replace('sts:', '')
        elem = element.find('.//' + simple_xpath)
        if elem is not None and elem.text:
            return elem.text.strip()

        return default

    def _get_decimal(self, xpath: str, default: float = 0.0, element=None) -> float:
        """Extrae un valor decimal de un elemento XML"""
        text = self._get_text(xpath, element=element)
        if not text:
            return default
        try:
            return float(text.replace(',', ''))
        except ValueError:
            return default

    def _formato_decimal(self, valor: float, decimales: int = 5) -> str:
        """Formatea un número decimal al formato colombiano (coma como decimal)"""
        return f"{valor:.{decimales}f}".replace('.', ',')

    def extraer_datos(self) -> List[Dict]:
        """Extrae datos en formato REGGIS para LACTALIS COMPRAS"""
        try:
            # Datos generales de la factura
            numero_factura = self._get_text('.//cbc:ID') or self._get_text('.//ID')
            fecha_emision = self._get_text('.//cbc:IssueDate') or self._get_text('.//IssueDate')
            fecha_vencimiento = self._get_text('.//cbc:DueDate') or self._get_text('.//DueDate')
            if not fecha_vencimiento:
                fecha_vencimiento = self._get_text('.//cbc:PaymentDueDate') or self._get_text('.//PaymentDueDate')

            # Datos del vendedor (quien emite la factura - proveedor de Lactalis)
            nit_vendedor = self._get_text('.//cac:AccountingSupplierParty//cbc:CompanyID') or \
                          self._get_text('.//AccountingSupplierParty//CompanyID')
            nombre_vendedor = self._get_text('.//cac:AccountingSupplierParty//cbc:RegistrationName') or \
                             self._get_text('.//AccountingSupplierParty//RegistrationName')
            ciudad_vendedor = self._get_text('.//cac:AccountingSupplierParty//cac:PhysicalLocation//cac:Address//cbc:CityName') or \
                             self._get_text('.//AccountingSupplierParty//Address//CityName')

            # Datos del comprador (Lactalis)
            nit_comprador = self._get_text('.//cac:AccountingCustomerParty//cbc:CompanyID') or \
                           self._get_text('.//AccountingCustomerParty//CompanyID')
            nombre_comprador = self._get_text('.//cac:AccountingCustomerParty//cbc:RegistrationName') or \
                              self._get_text('.//AccountingCustomerParty//RegistrationName')

            # Moneda
            moneda_documento = self._get_text('.//cbc:DocumentCurrencyCode') or \
                              self._get_text('.//DocumentCurrencyCode') or 'COP'
            codigo_moneda = CURRENCY_CODE_MAP.get(moneda_documento, '1')

            # TRM si es moneda extranjera
            trm = self._get_decimal('.//cac:PaymentExchangeRate//cbc:CalculationRate', 1.0)
            if trm == 0:
                trm = 1.0

            lineas_procesadas = []

            # Buscar líneas de la factura
            items = self.root.findall('.//cac:InvoiceLine', self.ns)
            if not items:
                items = self.root.findall('.//InvoiceLine')

            logger.info(f"Lactalis: Procesando {len(items)} líneas de la factura {numero_factura}")

            for idx, item in enumerate(items, 1):
                try:
                    # Descripción del producto
                    descripcion = self._get_text('.//cbc:Description', element=item) or \
                                 self._get_text('.//Description', element=item)

                    # Código del producto
                    codigo_producto = self._get_text('.//cac:SellersItemIdentification//cbc:ID', element=item) or \
                                     self._get_text('.//SellersItemIdentification//ID', element=item) or \
                                     self._get_text('.//cac:StandardItemIdentification//cbc:ID', element=item) or \
                                     self._get_text('.//StandardItemIdentification//ID', element=item)

                    # Cantidad y unidad de medida
                    cantidad_elem = item.find('.//cbc:InvoicedQuantity', self.ns)
                    if cantidad_elem is None:
                        cantidad_elem = item.find('.//InvoicedQuantity')

                    if cantidad_elem is not None:
                        cantidad_original = float(cantidad_elem.text or 0)
                        unidad_medida = cantidad_elem.get('unitCode', '') or 'Un'
                    else:
                        cantidad_original = 0.0
                        unidad_medida = 'Un'

                    # Mapeo de unidades de medida
                    unit_map = {
                        'KG': 'Kg', 'KGM': 'Kg', 'LBR': 'Kg',
                        'LTR': 'Lt', 'LT': 'Lt',
                        'NIU': 'Un', 'EA': 'Un', 'UN': 'Un'
                    }
                    unidad_medida_final = unit_map.get(unidad_medida, unidad_medida)

                    # Convertir libras a kilogramos si es necesario
                    if unidad_medida == 'LBR':
                        cantidad_convertida = cantidad_original / 2.20462
                        unidad_medida_final = 'Kg'
                    else:
                        cantidad_convertida = cantidad_original

                    # Precio unitario
                    precio_unitario = self._get_decimal('.//cac:Price//cbc:PriceAmount', element=item)
                    if precio_unitario == 0:
                        precio_unitario = self._get_decimal('.//PriceAmount', element=item)

                    # Si está en moneda extranjera, convertir a COP
                    if moneda_documento != 'COP':
                        precio_cop = precio_unitario * trm
                    else:
                        precio_cop = precio_unitario

                    # Total de la línea sin IVA
                    total_linea = self._get_decimal('.//cbc:LineExtensionAmount', element=item)
                    if total_linea == 0:
                        total_linea = self._get_decimal('.//LineExtensionAmount', element=item)
                        if total_linea == 0:
                            total_linea = cantidad_convertida * precio_cop

                    # IVA
                    porcentaje_iva = 0.0
                    iva_linea = 0.0

                    # Buscar información de impuestos
                    tax_total = item.find('.//cac:TaxTotal', self.ns)
                    if tax_total is None:
                        tax_total = item.find('.//TaxTotal')

                    if tax_total is not None:
                        porcentaje_iva = self._get_decimal('.//cbc:Percent', element=tax_total)
                        if porcentaje_iva == 0:
                            porcentaje_iva = self._get_decimal('.//Percent', element=tax_total)

                        iva_linea = self._get_decimal('.//cbc:TaxAmount', element=tax_total)
                        if iva_linea == 0:
                            iva_linea = self._get_decimal('.//TaxAmount', element=tax_total)

                    # Si no encontramos el IVA, calcularlo si tenemos el porcentaje
                    if iva_linea == 0 and porcentaje_iva > 0:
                        iva_linea = total_linea * (porcentaje_iva / 100)

                    # Total con IVA
                    total_con_iva = total_linea + iva_linea

                    linea = {
                        'numero_factura': numero_factura,
                        'nombre_producto': descripcion,
                        'codigo_subyacente': codigo_producto,
                        'unidad_medida': unidad_medida_final,
                        'cantidad': self._formato_decimal(cantidad_convertida, decimales=5),
                        'precio_unitario': self._formato_decimal(precio_cop, decimales=5),
                        'fecha_factura': fecha_emision,
                        'fecha_pago': fecha_vencimiento,
                        'nit_comprador': nit_comprador,
                        'nombre_comprador': nombre_comprador,
                        'nit_vendedor': nit_vendedor,
                        'nombre_vendedor': nombre_vendedor,
                        'principal': 'C',  # C para compras
                        'municipio': ciudad_vendedor,
                        'iva': str(int(porcentaje_iva)) if porcentaje_iva > 0 else '0',
                        'descripcion': descripcion,
                        'activa_factura': '1',
                        'activa_bodega': '1',
                        'incentivo': '',
                        'cantidad_original': self._formato_decimal(cantidad_original, decimales=5),
                        'moneda': codigo_moneda,
                        'total_sin_iva': total_linea,
                        'total_iva': iva_linea,
                        'total_con_iva': total_con_iva
                    }

                    lineas_procesadas.append(linea)

                except Exception as e:
                    logger.error(f"Error procesando línea {idx} de Lactalis: {str(e)}")
                    continue

            return lineas_procesadas

        except Exception as e:
            logger.error(f"Error al extraer datos de Lactalis: {str(e)}")
            return []
