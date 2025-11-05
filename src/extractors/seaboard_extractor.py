"""
Extractor de datos de facturas para SEABOARD
"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, List

from ..config.constants import NAMESPACES, CURRENCY_CODE_MAP

logger = logging.getLogger(__name__)


class FacturaExtractorSeaboard:
    """Extractor de datos de facturas para SEABOARD"""

    def __init__(self, xml_content: str):
        self.root = ET.fromstring(xml_content)
        self.ns = NAMESPACES

    def _get_text(self, xpath: str, default: str = "") -> str:
        """Extrae texto de un elemento XML"""
        element = self.root.find(xpath, self.ns)
        return element.text.strip() if element is not None and element.text else default

    def _get_decimal(self, xpath: str, default: float = 0.0) -> float:
        """Extrae un valor decimal de un elemento XML"""
        text = self._get_text(xpath)
        if not text:
            return default
        try:
            return float(text.replace(',', ''))
        except ValueError:
            return default

    def _formato_decimal(self, valor: float, decimales: int = 2) -> str:
        """Formatea un número decimal al formato colombiano (punto como separador de miles, coma como decimal)"""
        valor_str = f"{valor:.{decimales}f}"
        partes = valor_str.split('.')
        parte_entera = partes[0]
        parte_decimal = partes[1] if len(partes) > 1 else '00'

        parte_entera_formateada = ''
        for i, digito in enumerate(reversed(parte_entera)):
            if i > 0 and i % 3 == 0:
                parte_entera_formateada = '.' + parte_entera_formateada
            parte_entera_formateada = digito + parte_entera_formateada

        return f"{parte_entera_formateada},{parte_decimal}"

    def extraer_datos(self) -> List[Dict]:
        """Extrae datos en formato REGGIS para SEABOARD"""
        numero_factura = self._get_text('.//cbc:ID')
        fecha_emision = self._get_text('.//cbc:IssueDate')
        fecha_vencimiento = self._get_text('.//cbc:DueDate')

        nit_vendedor = self._get_text('.//cac:AccountingSupplierParty//cbc:CompanyID')
        nombre_vendedor = self._get_text('.//cac:AccountingSupplierParty//cbc:RegistrationName')
        ciudad_vendedor = self._get_text('.//cac:AccountingSupplierParty//cac:PhysicalLocation//cac:Address//cbc:CityName')

        nit_comprador = self._get_text('.//cac:AccountingCustomerParty//cbc:CompanyID')
        nombre_comprador = self._get_text('.//cac:AccountingCustomerParty//cbc:RegistrationName')

        moneda_documento = self._get_text('.//cbc:DocumentCurrencyCode', 'COP')
        trm = self._get_decimal('.//cac:PaymentExchangeRate//cbc:CalculationRate', 1.0)
        codigo_moneda = CURRENCY_CODE_MAP.get(moneda_documento, '1')

        porcentaje_iva = self._get_decimal('.//cac:TaxCategory//cbc:Percent', 5.0)

        lineas_procesadas = []
        items = self.root.findall('.//cac:InvoiceLine', self.ns)

        for idx, item in enumerate(items, 1):
            try:
                descripcion = item.find('.//cbc:Description', self.ns)
                nombre_producto = descripcion.text if descripcion is not None else ''

                codigo = item.find('.//cac:SellersItemIdentification//cbc:ID', self.ns)
                codigo_producto = codigo.text if codigo is not None else ''

                cantidad_elem = item.find('.//cbc:InvoicedQuantity', self.ns)
                cantidad_original = float(cantidad_elem.text) if cantidad_elem is not None else 0.0
                unidad_medida_original = cantidad_elem.get('unitCode', '') if cantidad_elem is not None else ''

                unidad_medida = unidad_medida_original
                if unidad_medida_original == 'TNE':
                    cantidad_en_kg = cantidad_original * 1000
                    unidad_medida = 'Kg'
                else:
                    cantidad_en_kg = cantidad_original

                precio_elem = item.find('.//cac:Price//cbc:PriceAmount', self.ns)
                precio_unitario_xml = float(precio_elem.text) if precio_elem is not None else 0.0

                if unidad_medida_original == 'TNE':
                    precio_por_kg = precio_unitario_xml / 1000
                else:
                    precio_por_kg = precio_unitario_xml

                if moneda_documento == 'USD':
                    precio_cop = precio_por_kg * trm
                else:
                    precio_cop = precio_por_kg

                total_sin_iva_linea = cantidad_en_kg * precio_cop
                iva_linea = total_sin_iva_linea * (porcentaje_iva / 100)
                total_con_iva_linea = total_sin_iva_linea + iva_linea

                linea = {
                    'numero_factura': numero_factura,
                    'nombre_producto': nombre_producto,
                    'codigo_subyacente': codigo_producto,
                    'unidad_medida': unidad_medida,
                    'cantidad': self._formato_decimal(cantidad_en_kg, decimales=5),
                    'precio_unitario': self._formato_decimal(precio_cop, decimales=6),
                    'fecha_factura': fecha_emision,
                    'fecha_pago': fecha_vencimiento,
                    'nit_comprador': nit_comprador,
                    'nombre_comprador': nombre_comprador,
                    'nit_vendedor': nit_vendedor,
                    'nombre_vendedor': nombre_vendedor,
                    'principal': 'V',
                    'municipio': ciudad_vendedor,
                    'iva': str(int(porcentaje_iva)),
                    'descripcion': nombre_producto,
                    'activa_factura': 'SI',
                    'activa_bodega': '',
                    'incentivo': '',
                    'cantidad_original': self._formato_decimal(cantidad_original, decimales=5),
                    'moneda': codigo_moneda,
                    'total_sin_iva': total_sin_iva_linea,
                    'total_iva': iva_linea,
                    'total_con_iva': total_con_iva_linea
                }

                lineas_procesadas.append(linea)

            except Exception as e:
                logger.error(f"Error procesando linea {idx}: {str(e)}")
                continue

        return lineas_procesadas
