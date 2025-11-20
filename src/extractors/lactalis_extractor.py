"""
Extractor de datos de facturas electrónicas XML para LACTALIS COMPRAS
Lee archivos XML directamente desde ZIPs sin necesidad de extraer
"""

import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Optional
from decimal import Decimal, InvalidOperation

from config.constants import NAMESPACES, CURRENCY_CODE_MAP, UNIT_MAP, LACTALIS_CONFIG

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
            logger.warning(f"{self.archivo_nombre}: root es None")
            return []

        try:
            # Debug: Log del tag raíz
            logger.debug(f"{self.archivo_nombre}: Tag raiz = {self.root.tag}")

            # Extraer datos generales de la factura
            numero_factura = self._extraer_numero_factura()
            fecha_factura = self._extraer_fecha_factura()
            fecha_pago = self._extraer_fecha_vencimiento()
            moneda = self._extraer_moneda()

            logger.debug(
                f"{self.archivo_nombre}: Factura={numero_factura}, "
                f"Fecha={fecha_factura}, Moneda={moneda}"
            )

            # Datos del comprador (Lactalis) - VALORES FIJOS
            nit_comprador = LACTALIS_CONFIG['nit_comprador']
            nombre_comprador = LACTALIS_CONFIG['nombre_comprador']
            municipio = self._extraer_municipio()

            # Extraer datos del vendedor (proveedor)
            # NOTA: Algunos XMLs (ej: DSP*) no tienen NIT de vendedor
            nit_vendedor = self._extraer_nit_vendedor() or ""  # Permitir vacío
            nombre_vendedor = self._extraer_nombre_vendedor()

            logger.debug(
                f"{self.archivo_nombre}: Comprador={nombre_comprador} ({nit_comprador}), "
                f"Vendedor={nombre_vendedor} ({nit_vendedor if nit_vendedor else 'SIN NIT'})"
            )

            # Extraer líneas de productos - intentar con y sin namespace
            invoice_lines = self.root.findall('.//cac:InvoiceLine', NAMESPACES)

            # Si no encuentra con namespace, intentar sin namespace
            if not invoice_lines:
                logger.warning(f"{self.archivo_nombre}: No se encontraron InvoiceLines con namespace, intentando sin namespace")
                # Buscar cualquier elemento que termine en InvoiceLine
                invoice_lines = self.root.findall('.//*[local-name()="InvoiceLine"]')

            logger.debug(f"{self.archivo_nombre}: Se encontraron {len(invoice_lines)} lineas de factura")

            if not invoice_lines:
                logger.warning(
                    f"{self.archivo_nombre}: No se encontraron lineas de productos. "
                    f"Esto puede ser un AttachedDocument o un tipo de documento diferente."
                )
                return []

            lineas = []
            for idx, line in enumerate(invoice_lines, 1):
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
                else:
                    logger.warning(f"{self.archivo_nombre}: Linea {idx} no se pudo extraer")

            logger.info(f"Extraidas {len(lineas)} lineas de {self.archivo_nombre}")
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
            # VALORES FIJOS DE LACTALIS (según especificaciones del cliente)
            nombre_producto_text = LACTALIS_CONFIG['nombre_producto']  # Siempre "LECHE CRUDA"
            codigo_text = LACTALIS_CONFIG['codigo_subyacente']  # Siempre "SPN-1"
            unidad_medida = LACTALIS_CONFIG['unidad_medida']  # Siempre "Lt"

            # Cantidad (sí se extrae del XML)
            cantidad_element = line_element.find('.//cbc:InvoicedQuantity', NAMESPACES)
            if cantidad_element is None:
                # Fallback sin namespace
                cantidad_element = line_element.find('.//*[local-name()="InvoicedQuantity"]')

            cantidad = self._parse_decimal(cantidad_element.text if cantidad_element is not None else "0")
            cantidad_original = cantidad  # Guardar cantidad original

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

            # Construir línea en formato REGGIS con valores fijos de Lactalis
            linea_reggis = {
                'numero_factura': numero_factura,
                'nombre_producto': nombre_producto_text,  # FIJO: "LECHE CRUDA"
                'codigo_subyacente': codigo_text,  # FIJO: "SPN-1"
                'unidad_medida': unidad_medida,  # FIJO: "Lt"
                'cantidad': cantidad_fmt,
                'precio_unitario': precio_unitario_fmt,
                'fecha_factura': fecha_factura,
                'fecha_pago': fecha_pago,
                'nit_comprador': nit_comprador,  # FIJO: NIT de Lactalis
                'nombre_comprador': nombre_comprador,  # FIJO: "LACTALIS"
                'nit_vendedor': nit_vendedor,  # Puede estar vacío en algunos XMLs
                'nombre_vendedor': nombre_vendedor,
                'principal': LACTALIS_CONFIG['principal'],  # FIJO: "C"
                'municipio': municipio,
                'iva': str(int(iva_percent)),
                'descripcion': LACTALIS_CONFIG['descripcion'],  # FIJO: vacío
                'activa_factura': LACTALIS_CONFIG['activa_factura'],  # FIJO: "1"
                'activa_bodega': LACTALIS_CONFIG['activa_bodega'],  # FIJO: "1"
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
