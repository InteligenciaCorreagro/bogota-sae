"""
Extractor de datos de facturas electrónicas XML para LACTALIS COMPRAS
Lee archivos XML directamente desde ZIPs sin necesidad de extraer
"""

import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Optional
from decimal import Decimal, InvalidOperation

from config.constants import NAMESPACES, CURRENCY_CODE_MAP, UNIT_MAP

logger = logging.getLogger(__name__)


class FacturaExtractorLactalis:
    """
    Extractor de facturas XML para LACTALIS COMPRAS

    Extrae información de facturas electrónicas en formato UBL 2.1
    y la transforma al formato REGGIS estándar
    """

    def __init__(self, xml_content: str, archivo_nombre: str = ""):
        """
        Inicializa el extractor con contenido XML

        Args:
            xml_content: Contenido del archivo XML como string
            archivo_nombre: Nombre del archivo para logging
        """
        self.xml_content = xml_content
        self.archivo_nombre = archivo_nombre
        self.root = None

        try:
            self.root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Error parseando XML {archivo_nombre}: {str(e)}")
            raise

    def extraer_datos(self) -> List[Dict]:
        """
        Extrae los datos de la factura y retorna lista de líneas en formato REGGIS

        Returns:
            Lista de diccionarios con datos de cada línea de la factura
        """
        if self.root is None:
            return []

        try:
            # Extraer datos generales de la factura
            numero_factura = self._extraer_numero_factura()
            fecha_factura = self._extraer_fecha_factura()
            fecha_pago = self._extraer_fecha_vencimiento()
            moneda = self._extraer_moneda()

            # Extraer datos del comprador (Lactalis)
            nit_comprador = self._extraer_nit_comprador()
            nombre_comprador = self._extraer_nombre_comprador()
            municipio = self._extraer_municipio()

            # Extraer datos del vendedor (proveedor)
            nit_vendedor = self._extraer_nit_vendedor()
            nombre_vendedor = self._extraer_nombre_vendedor()

            # Extraer líneas de productos
            lineas = []
            invoice_lines = self.root.findall('.//cac:InvoiceLine', NAMESPACES)

            for line in invoice_lines:
                linea_data = self._extraer_linea_producto(
                    line,
                    numero_factura,
                    fecha_factura,
                    fecha_pago,
                    nit_comprador,
                    nombre_comprador,
                    nit_vendedor,
                    nombre_vendedor,
                    municipio,
                    moneda
                )

                if linea_data:
                    lineas.append(linea_data)

            logger.info(f"Extraídas {len(lineas)} líneas de {self.archivo_nombre}")
            return lineas

        except Exception as e:
            logger.error(f"Error extrayendo datos de {self.archivo_nombre}: {str(e)}", exc_info=True)
            return []

    def _extraer_numero_factura(self) -> str:
        """Extrae el número de factura"""
        numero = self.root.find('.//cbc:ID', NAMESPACES)
        return numero.text.strip() if numero is not None and numero.text else ""

    def _extraer_fecha_factura(self) -> str:
        """Extrae la fecha de emisión de la factura"""
        fecha = self.root.find('.//cbc:IssueDate', NAMESPACES)
        return fecha.text.strip() if fecha is not None and fecha.text else ""

    def _extraer_fecha_vencimiento(self) -> str:
        """Extrae la fecha de vencimiento/pago"""
        # Intentar PaymentDueDate primero
        fecha = self.root.find('.//cbc:DueDate', NAMESPACES)
        if fecha is None:
            fecha = self.root.find('.//cbc:PaymentDueDate', NAMESPACES)

        if fecha is not None and fecha.text:
            return fecha.text.strip()

        # Si no hay fecha de vencimiento, usar fecha de factura
        return self._extraer_fecha_factura()

    def _extraer_moneda(self) -> str:
        """Extrae el código de moneda y lo convierte al formato REGGIS"""
        moneda_element = self.root.find('.//cbc:DocumentCurrencyCode', NAMESPACES)
        if moneda_element is not None and moneda_element.text:
            codigo_moneda = moneda_element.text.strip().upper()
            return CURRENCY_CODE_MAP.get(codigo_moneda, '1')  # Default COP = 1
        return '1'

    def _extraer_nit_comprador(self) -> str:
        """Extrae el NIT del comprador (Lactalis)"""
        nit = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID', NAMESPACES)
        if nit is not None and nit.text:
            return nit.text.strip()

        # Alternativa
        nit = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID', NAMESPACES)
        return nit.text.strip() if nit is not None and nit.text else ""

    def _extraer_nombre_comprador(self) -> str:
        """Extrae el nombre del comprador (Lactalis)"""
        nombre = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName', NAMESPACES)
        if nombre is None:
            nombre = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name', NAMESPACES)
        return nombre.text.strip() if nombre is not None and nombre.text else ""

    def _extraer_municipio(self) -> str:
        """Extrae el municipio del comprador"""
        municipio = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName', NAMESPACES)
        if municipio is None:
            municipio = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name', NAMESPACES)
        return municipio.text.strip() if municipio is not None and municipio.text else ""

    def _extraer_nit_vendedor(self) -> str:
        """Extrae el NIT del vendedor (proveedor)"""
        nit = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID', NAMESPACES)
        if nit is not None and nit.text:
            return nit.text.strip()

        # Alternativa
        nit = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID', NAMESPACES)
        return nit.text.strip() if nit is not None and nit.text else ""

    def _extraer_nombre_vendedor(self) -> str:
        """Extrae el nombre del vendedor (proveedor)"""
        nombre = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName', NAMESPACES)
        if nombre is None:
            nombre = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name', NAMESPACES)
        return nombre.text.strip() if nombre is not None and nombre.text else ""

    def _extraer_linea_producto(self, line_element, numero_factura: str, fecha_factura: str,
                                 fecha_pago: str, nit_comprador: str, nombre_comprador: str,
                                 nit_vendedor: str, nombre_vendedor: str, municipio: str,
                                 moneda: str) -> Optional[Dict]:
        """
        Extrae los datos de una línea de producto

        Args:
            line_element: Elemento XML InvoiceLine
            Resto: Datos generales de la factura

        Returns:
            Diccionario con datos de la línea en formato REGGIS
        """
        try:
            # Nombre del producto
            nombre_producto = line_element.find('.//cac:Item/cbc:Description', NAMESPACES)
            if nombre_producto is None:
                nombre_producto = line_element.find('.//cac:Item/cbc:Name', NAMESPACES)
            nombre_producto_text = nombre_producto.text.strip() if nombre_producto is not None and nombre_producto.text else ""

            # Código del producto
            codigo = line_element.find('.//cac:Item/cac:SellersItemIdentification/cbc:ID', NAMESPACES)
            if codigo is None:
                codigo = line_element.find('.//cac:Item/cac:StandardItemIdentification/cbc:ID', NAMESPACES)
            codigo_text = codigo.text.strip() if codigo is not None and codigo.text else ""

            # Cantidad
            cantidad_element = line_element.find('.//cbc:InvoicedQuantity', NAMESPACES)
            cantidad = self._parse_decimal(cantidad_element.text if cantidad_element is not None else "0")
            cantidad_original = cantidad  # Guardar cantidad original

            # Unidad de medida
            unidad_raw = cantidad_element.get('unitCode', 'UN') if cantidad_element is not None else 'UN'
            unidad_medida = UNIT_MAP.get(unidad_raw.upper(), 'Un')

            # Precio unitario
            precio_element = line_element.find('.//cac:Price/cbc:PriceAmount', NAMESPACES)
            precio_unitario = self._parse_decimal(precio_element.text if precio_element is not None else "0")

            # Totales
            total_sin_iva_element = line_element.find('.//cbc:LineExtensionAmount', NAMESPACES)
            total_sin_iva = self._parse_decimal(total_sin_iva_element.text if total_sin_iva_element is not None else "0")

            # IVA
            iva_percent = self._extraer_iva_linea(line_element)
            total_iva = total_sin_iva * (iva_percent / Decimal('100'))
            total_con_iva = total_sin_iva + total_iva

            # Formatear números al estándar colombiano (coma como separador decimal)
            cantidad_fmt = self._formatear_numero(cantidad)
            cantidad_original_fmt = self._formatear_numero(cantidad_original)
            precio_unitario_fmt = self._formatear_numero(precio_unitario)
            total_sin_iva_fmt = self._formatear_numero(total_sin_iva)
            total_iva_fmt = self._formatear_numero(total_iva)
            total_con_iva_fmt = self._formatear_numero(total_con_iva)

            # Construir línea en formato REGGIS
            linea_reggis = {
                'numero_factura': numero_factura,
                'nombre_producto': nombre_producto_text,
                'codigo_subyacente': codigo_text,
                'unidad_medida': unidad_medida,
                'cantidad': cantidad_fmt,
                'precio_unitario': precio_unitario_fmt,
                'fecha_factura': fecha_factura,
                'fecha_pago': fecha_pago,
                'nit_comprador': nit_comprador,
                'nombre_comprador': nombre_comprador,
                'nit_vendedor': nit_vendedor,
                'nombre_vendedor': nombre_vendedor,
                'principal': 'C',  # Lactalis es Comprador
                'municipio': municipio,
                'iva': str(int(iva_percent)),
                'descripcion': nombre_producto_text,
                'activa_factura': '',
                'activa_bodega': '',
                'incentivo': '',
                'cantidad_original': cantidad_original_fmt,
                'moneda': moneda,
                'total_sin_iva': total_sin_iva_fmt,
                'total_iva': total_iva_fmt,
                'total_con_iva': total_con_iva_fmt
            }

            return linea_reggis

        except Exception as e:
            logger.error(f"Error extrayendo línea de producto: {str(e)}", exc_info=True)
            return None

    def _extraer_iva_linea(self, line_element) -> Decimal:
        """Extrae el porcentaje de IVA de una línea"""
        # Buscar en TaxTotal
        iva_element = line_element.find('.//cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', NAMESPACES)
        if iva_element is not None and iva_element.text:
            return self._parse_decimal(iva_element.text)

        # Alternativa: buscar en AllowanceCharge
        iva_element = line_element.find('.//cac:AllowanceCharge/cac:TaxCategory/cbc:Percent', NAMESPACES)
        if iva_element is not None and iva_element.text:
            return self._parse_decimal(iva_element.text)

        # Default: 19% (IVA común en Colombia)
        return Decimal('19')

    def _parse_decimal(self, value: str) -> Decimal:
        """
        Parsea un string a Decimal de forma segura

        Args:
            value: String con número

        Returns:
            Decimal
        """
        try:
            # Limpiar el string
            cleaned = value.strip().replace(',', '.')
            return Decimal(cleaned)
        except (InvalidOperation, ValueError, AttributeError):
            return Decimal('0')

    def _formatear_numero(self, numero: Decimal, decimales: int = 5) -> str:
        """
        Formatea un número Decimal al formato colombiano (coma como separador decimal)

        Args:
            numero: Número a formatear
            decimales: Número de decimales

        Returns:
            String con número formateado
        """
        # Redondear a N decimales
        formato = f"{{:.{decimales}f}}"
        numero_str = formato.format(numero)

        # Reemplazar punto por coma (estándar colombiano)
        return numero_str.replace('.', ',')
