"""
Extractor de datos de facturas electrónicas XML para LACTALIS VENTAS
Optimizado para procesar grandes volúmenes (20,000+ XML)
Con validaciones estrictas de reglas de negocio

ACTUALIZACIÓN: Detecta automáticamente el vendedor (Lactalis o Proleche) del XML
"""

import xml.etree.ElementTree as ET
import logging
import re
from typing import List, Dict, Optional, Tuple
from decimal import Decimal, InvalidOperation

# Intentar importar desde el proyecto, si no, usar constantes inline
try:
    from src.config.constants import NAMESPACES, CURRENCY_CODE_MAP, UNIT_MAP, LACTALIS_VENTAS_CONFIG
except ImportError:
    # Configuración inline para modo standalone
    NAMESPACES = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
    }

    CURRENCY_CODE_MAP = {
        'COP': '1',
        'USD': '2',
        'EUR': '3'
    }

    UNIT_MAP = {
        'KG': 'Kg',
        'KGM': 'Kg',
        'LBR': 'Kg',
        'LTR': 'Lt',
        'LT': 'Lt',
        'NIU': 'Un',
        'EA': 'Un',
        'EV': 'Un',
        'JR': 'Un',
        'UN': 'Un'
    }

    LACTALIS_VENTAS_CONFIG = {
        # NOTA: El vendedor se detecta automáticamente del XML
        # Puede ser Lactalis o Proleche:
        # - Lactalis: NIT 800245795, nombre 'LACTALIS COLOMBIA S.A.S'
        # - Proleche: NIT 890903711, nombre 'PROCESADORA DE LECHES S.A. - PROLECHE S.A.'
        
        'activa_factura': '1',
        'activa_bodega': '1',
        'principal': 'V',
        'batch_size': 500,
    }

logger = logging.getLogger(__name__)


class ValidacionFacturaError(Exception):
    """Excepción para facturas que no cumplen reglas de negocio"""
    pass


class FacturaExtractorLactalisVentas:
    """
    Extractor de facturas XML para LACTALIS VENTAS con validaciones estrictas
    
    REGLAS DE NEGOCIO:
    1. Solo facturas (Invoice), NO notas crédito/débito
    2. Cantidad > 0
    3. Precio unitario > 0
    4. Total > 0
    5. Todos los valores numéricos deben ser válidos
    
    VENDEDORES SOPORTADOS:
    - Lactalis: NIT 800245795
    - Proleche: NIT 890903711
    (Se detecta automáticamente del XML)
    """

    def __init__(self, xml_content: str, archivo_nombre: str = ""):
        """
        Inicializa el extractor con contenido XML - CON MÁXIMA PROTECCIÓN
        
        Args:
            xml_content: Contenido del archivo XML como string
            archivo_nombre: Nombre del archivo para logging
        """
        self.xml_content = xml_content
        self.archivo_nombre = archivo_nombre
        self.root = None
        self.tipo_documento = None

        try:
            # Intentar parsear el XML
            self.root = ET.fromstring(xml_content)
            self._detectar_tipo_documento()
        except ET.ParseError as e:
            logger.error(f"Error parseando XML {archivo_nombre}: {str(e)}")
            # No hacer raise - dejar que tipo_documento sea None
            self.tipo_documento = "ParseError"
        except Exception as e:
            logger.error(f"Error inesperado parseando XML {archivo_nombre}: {type(e).__name__}: {str(e)}")
            self.tipo_documento = "UnknownError"

    def _detectar_tipo_documento(self):
        """Detecta el tipo de documento (Invoice, CreditNote, DebitNote, AttachedDocument)"""
        root_tag = self.root.tag
        
        # Eliminar namespace del tag
        if '}' in root_tag:
            root_tag = root_tag.split('}')[1]
        
        self.tipo_documento = root_tag
        logger.debug(f"{self.archivo_nombre}: Tipo de documento detectado: {self.tipo_documento}")

    def _extraer_invoice_de_attached_document(self) -> Optional[str]:
        """
        Extrae el XML de la factura desde un AttachedDocument
        
        Returns:
            XML de la factura si es AttachedDocument, None si no lo es
        """
        try:
            # Opción 1: Buscar en ExternalReference/Description (CDATA)
            description = self.root.find('.//cac:ExternalReference/cbc:Description', NAMESPACES)
            if description is not None and description.text:
                xml_text = description.text.strip()
                if xml_text:
                    logger.debug(f"{self.archivo_nombre}: XML interno encontrado en ExternalReference/Description")
                    return xml_text
            
            # Opción 2: Buscar en Attachment/ExternalReference/Description
            description = self.root.find('.//cac:Attachment/cac:ExternalReference/cbc:Description', NAMESPACES)
            if description is not None and description.text:
                xml_text = description.text.strip()
                if xml_text:
                    logger.debug(f"{self.archivo_nombre}: XML interno encontrado en Attachment/ExternalReference/Description")
                    return xml_text
            
            # Opción 3: Buscar sin namespace
            for elem in self.root.iter():
                if elem.tag.endswith('Description') and elem.text and '<' in elem.text:
                    xml_text = elem.text.strip()
                    if xml_text:
                        logger.debug(f"{self.archivo_nombre}: XML interno encontrado iterando elementos")
                        return xml_text
            
            logger.warning(f"{self.archivo_nombre}: AttachedDocument no contiene XML interno")
            return None
            
        except Exception as e:
            logger.error(f"{self.archivo_nombre}: Error extrayendo XML interno: {str(e)}")
            return None

    def validar_factura(self) -> bool:
        """
        Valida que el documento cumpla las reglas de negocio
        
        Returns:
            True si es válido, False si no
            
        Raises:
            ValidacionFacturaError: Si no cumple las reglas
        """
        # REGLA 1: Solo facturas (Invoice)
        if self.tipo_documento == 'AttachedDocument':
            # Extraer y procesar el XML interno
            invoice_xml = self._extraer_invoice_de_attached_document()
            if invoice_xml:
                # Re-procesar el XML interno
                try:
                    self.root = ET.fromstring(invoice_xml)
                    self._detectar_tipo_documento()
                except Exception as e:
                    raise ValidacionFacturaError(f"Error procesando XML interno: {str(e)}")
            else:
                # No se encontró XML interno en AttachedDocument
                raise ValidacionFacturaError(
                    f"AttachedDocument no contiene XML interno válido"
                )
        
        if self.tipo_documento != 'Invoice':
            raise ValidacionFacturaError(
                f"No es una factura (es {self.tipo_documento}). Solo se procesan facturas (Invoice)."
            )
        
        return True

    def extraer_datos(self) -> List[Dict]:
        """
        Extrae los datos de la factura y retorna lista de líneas en formato REGGIS
        
        Returns:
            Lista de diccionarios con datos de cada línea de la factura
            
        Raises:
            ValidacionFacturaError: Si no cumple las reglas de negocio
        """
        # Validación previa: ¿se pudo parsear el XML?
        if self.root is None:
            logger.error(f"{self.archivo_nombre}: No se pudo parsear el XML")
            return []
        
        if self.tipo_documento in ["ParseError", "UnknownError", None]:
            logger.error(f"{self.archivo_nombre}: Tipo de documento inválido: {self.tipo_documento}")
            return []
        
        # Validar que sea una factura válida
        try:
            self.validar_factura()
        except ValidacionFacturaError as e:
            logger.warning(f"{self.archivo_nombre}: {str(e)}")
            return []  # Retornar lista vacía, no procesar
        except Exception as e:
            logger.error(f"{self.archivo_nombre}: Error en validación: {str(e)}")
            return []

        try:
            # Extraer datos generales de la factura
            numero_factura = self._extraer_numero_factura()
            fecha_factura = self._extraer_fecha_factura()
            fecha_pago = self._extraer_fecha_vencimiento()
            moneda = self._extraer_moneda()

            logger.debug(
                f"{self.archivo_nombre}: Factura={numero_factura}, "
                f"Fecha={fecha_factura}, Moneda={moneda}"
            )

            # Extraer datos del vendedor (puede ser Lactalis o Proleche)
            # IMPORTANTE: Se extrae del XML, NO valores fijos
            nit_vendedor = self._extraer_nit_vendedor()
            nombre_vendedor = self._extraer_nombre_vendedor()
            
            # Extraer datos del comprador (cliente)
            nit_comprador = self._extraer_nit_comprador()
            nombre_comprador = self._extraer_nombre_comprador()
            municipio = self._extraer_municipio()

            logger.debug(
                f"{self.archivo_nombre}: Vendedor={nombre_vendedor} ({nit_vendedor}), "
                f"Comprador={nombre_comprador} ({nit_comprador})"
            )

            # Extraer líneas de productos
            invoice_lines = self.root.findall('.//cac:InvoiceLine', NAMESPACES)

            if not invoice_lines:
                # Intentar sin namespace
                invoice_lines = self.root.findall('.//*[local-name()="InvoiceLine"]')

            logger.debug(f"{self.archivo_nombre}: Se encontraron {len(invoice_lines)} líneas de factura")

            if not invoice_lines:
                logger.warning(f"{self.archivo_nombre}: No se encontraron líneas de productos")
                return []

            lineas = []
            lineas_rechazadas = 0
            
            for idx, line in enumerate(invoice_lines, 1):
                try:
                    linea_data = self._extraer_linea_producto(
                        line,
                        numero_factura,
                        fecha_factura,
                        fecha_pago,
                        nit_vendedor,
                        nombre_vendedor,
                        nit_comprador,
                        nombre_comprador,
                        municipio,
                        moneda
                    )

                    if linea_data:
                        lineas.append(linea_data)
                    else:
                        lineas_rechazadas += 1
                        
                except ValidacionFacturaError as e:
                    logger.warning(f"{self.archivo_nombre}: Línea {idx} rechazada - {str(e)}")
                    lineas_rechazadas += 1
                except Exception as e:
                    logger.error(f"{self.archivo_nombre}: Error en línea {idx} - {str(e)}", exc_info=True)
                    lineas_rechazadas += 1

            if lineas_rechazadas > 0:
                logger.info(
                    f"{self.archivo_nombre}: {len(lineas)} líneas procesadas, "
                    f"{lineas_rechazadas} líneas rechazadas"
                )
            else:
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
        """Extrae el NIT del comprador (cliente)"""
        nit = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID', NAMESPACES)
        if nit is not None and nit.text:
            return nit.text.strip()

        # Alternativa
        nit = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID', NAMESPACES)
        return nit.text.strip() if nit is not None and nit.text else ""

    def _extraer_nombre_comprador(self) -> str:
        """Extrae el nombre del comprador (cliente)"""
        nombre = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName', NAMESPACES)
        if nombre is None:
            nombre = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name', NAMESPACES)
        return nombre.text.strip() if nombre is not None and nombre.text else ""

    def _extraer_nit_vendedor(self) -> str:
        """
        Extrae el NIT del vendedor (puede ser Lactalis o Proleche)
        Se extrae dinámicamente del XML
        
        Vendedores posibles:
        - Lactalis: 800245795
        - Proleche: 890903711
        """
        # Buscar en AccountingSupplierParty (vendedor)
        nit = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID', NAMESPACES)
        if nit is not None and nit.text:
            return nit.text.strip()

        # Alternativa en PartyIdentification
        nit = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID', NAMESPACES)
        if nit is not None and nit.text:
            return nit.text.strip()

        # Buscar iterando sin namespace
        for elem in self.root.iter():
            if elem.tag.endswith('AccountingSupplierParty'):
                for party_elem in elem.iter():
                    if party_elem.tag.endswith('CompanyID'):
                        if party_elem.text:
                            return party_elem.text.strip()

        return ""

    def _extraer_nombre_vendedor(self) -> str:
        """
        Extrae el nombre del vendedor (puede ser Lactalis o Proleche)
        Se extrae dinámicamente del XML
        
        Vendedores posibles:
        - LACTALIS COLOMBIA S.A.S
        - PROCESADORA DE LECHES S.A. - PROLECHE S.A.
        """
        # Buscar en PartyLegalEntity
        nombre = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName', NAMESPACES)
        if nombre is not None and nombre.text:
            return nombre.text.strip()

        # Alternativa en PartyName
        nombre = self.root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name', NAMESPACES)
        if nombre is not None and nombre.text:
            return nombre.text.strip()

        # Buscar iterando sin namespace
        for elem in self.root.iter():
            if elem.tag.endswith('AccountingSupplierParty'):
                for party_elem in elem.iter():
                    if party_elem.tag.endswith('RegistrationName'):
                        if party_elem.text:
                            return party_elem.text.strip()

        return ""

    def _extraer_municipio(self) -> str:
        """Extrae el municipio del comprador"""
        municipio = self.root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName', NAMESPACES)
        return municipio.text.strip() if municipio is not None and municipio.text else ""

    def _extraer_linea_producto(self, line_element, numero_factura: str, fecha_factura: str,
                                 fecha_pago: str, nit_vendedor: str, nombre_vendedor: str,
                                 nit_comprador: str, nombre_comprador: str, municipio: str,
                                 moneda: str) -> Optional[Dict]:
        """
        Extrae los datos de una línea de producto con validaciones estrictas
        
        Args:
            line_element: Elemento XML InvoiceLine
            Resto: Datos generales de la factura

        Returns:
            Diccionario con datos de la línea en formato REGGIS o None si no pasa validaciones
            
        Raises:
            ValidacionFacturaError: Si no cumple las reglas de negocio
        """
        try:
            # Extraer nombre de producto
            nombre_element = line_element.find('.//cac:Item/cbc:Description', NAMESPACES)
            if nombre_element is None:
                # Buscar iterando sin XPath complejo
                for item in line_element.iter():
                    if item.tag.endswith('Item'):
                        for child in item:
                            if child.tag.endswith('Description'):
                                nombre_element = child
                                break
            nombre_producto = nombre_element.text.strip() if nombre_element is not None and nombre_element.text else ""

            # Extraer código
            codigo_element = line_element.find('.//cac:Item/cac:SellersItemIdentification/cbc:ID', NAMESPACES)
            if codigo_element is None:
                # Buscar iterando sin XPath complejo
                for item in line_element.iter():
                    if item.tag.endswith('SellersItemIdentification'):
                        for child in item:
                            if child.tag.endswith('ID'):
                                codigo_element = child
                                break
            codigo = codigo_element.text.strip() if codigo_element is not None and codigo_element.text else ""

            # Cantidad
            cantidad_element = line_element.find('.//cbc:InvoicedQuantity', NAMESPACES)
            if cantidad_element is None:
                # Buscar iterando
                for elem in line_element.iter():
                    if elem.tag.endswith('InvoicedQuantity'):
                        cantidad_element = elem
                        break
            
            cantidad = self._parse_decimal(cantidad_element.text if cantidad_element is not None else "0")
            unidad_medida_code = cantidad_element.get('unitCode', '') if cantidad_element is not None else ''

            # VALIDACIÓN: Cantidad debe ser > 0
            if cantidad <= Decimal('0'):
                raise ValidacionFacturaError(f"Cantidad inválida: {cantidad} (debe ser > 0)")

            # Precio unitario
            precio_element = line_element.find('.//cac:Price/cbc:PriceAmount', NAMESPACES)
            precio_unitario = self._parse_decimal(precio_element.text if precio_element is not None else "0")

            # VALIDACIÓN: Precio unitario debe ser > 0
            if precio_unitario <= Decimal('0'):
                raise ValidacionFacturaError(f"Precio unitario inválido: {precio_unitario} (debe ser > 0)")

            # Totales
            total_sin_iva_element = line_element.find('.//cbc:LineExtensionAmount', NAMESPACES)
            total_sin_iva = self._parse_decimal(total_sin_iva_element.text if total_sin_iva_element is not None else "0")

            # VALIDACIÓN: Total debe ser > 0
            if total_sin_iva <= Decimal('0'):
                raise ValidacionFacturaError(f"Total sin IVA inválido: {total_sin_iva} (debe ser > 0)")

            # IVA
            iva_percent = self._extraer_iva_linea(line_element)
            total_iva = total_sin_iva * (iva_percent / Decimal('100'))
            total_con_iva = total_sin_iva + total_iva

            # Unidad de medida original (mapear a estándar REGGIS)
            unidad_original = UNIT_MAP.get(unidad_medida_code, unidad_medida_code)

            cantidad_original = cantidad
            cantidad_convertida, unidad_destino, factor, ok, error = self._convertir_cantidad_bmc(
                cantidad_original,
                unidad_original,
                nombre_producto
            )

            if not ok:
                logger.info(
                    f"{self.archivo_nombre}: Conversion no aplicada ({error}) - "
                    f"Producto: {nombre_producto}"
                )

            cantidad = cantidad_convertida
            unidad_medida = unidad_destino

            # Formatear números al estándar colombiano (coma como separador decimal)
            cantidad_fmt = self._formatear_numero(cantidad)
            precio_unitario_fmt = self._formatear_numero(precio_unitario)
            total_sin_iva_fmt = self._formatear_numero(total_sin_iva)
            total_iva_fmt = self._formatear_numero(total_iva)
            total_con_iva_fmt = self._formatear_numero(total_con_iva)
            cantidad_original_fmt = self._formatear_numero(cantidad_original)

            # Construir línea en formato REGGIS
            linea_reggis = {
                'numero_factura': numero_factura,
                'nombre_producto': nombre_producto,
                'codigo_subyacente': codigo,
                'unidad_medida': unidad_medida,
                'cantidad': cantidad_fmt,
                'precio_unitario': precio_unitario_fmt,
                'fecha_factura': fecha_factura,
                'fecha_pago': fecha_pago,
                'nit_comprador': nit_comprador,
                'nombre_comprador': nombre_comprador,
                'nit_vendedor': nit_vendedor,  # Dinámico: Lactalis o Proleche
                'nombre_vendedor': nombre_vendedor,  # Dinámico: Lactalis o Proleche
                'principal': LACTALIS_VENTAS_CONFIG['principal'],  # FIJO: "V"
                'municipio': municipio,
                'iva': str(int(iva_percent)),
                'descripcion': nombre_producto,
                'activa_factura': LACTALIS_VENTAS_CONFIG['activa_factura'],  # FIJO: "1"
                'activa_bodega': LACTALIS_VENTAS_CONFIG['activa_bodega'],  # FIJO: "1"
                'incentivo': '',
                'cantidad_original': cantidad_original_fmt,
                'moneda': moneda,
                'total_sin_iva': total_sin_iva_fmt,
                'total_iva': total_iva_fmt,
                'total_con_iva': total_con_iva_fmt
            }

            return linea_reggis

        except ValidacionFacturaError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            logger.error(f"Error extrayendo línea de producto: {str(e)}", exc_info=True)
            return None

    def _extraer_iva_linea(self, line_element) -> Decimal:
        """Extrae el porcentaje de IVA de una línea"""
        # Priorizar IVA (TaxScheme ID=01 o Name=IVA) dentro de TaxSubtotal de la linea
        for tax_subtotal in line_element.findall('.//cac:TaxTotal/cac:TaxSubtotal', NAMESPACES):
            scheme_id = tax_subtotal.find('.//cac:TaxScheme/cbc:ID', NAMESPACES)
            scheme_name = tax_subtotal.find('.//cac:TaxScheme/cbc:Name', NAMESPACES)
            percent = tax_subtotal.find('.//cac:TaxCategory/cbc:Percent', NAMESPACES)

            scheme_id_text = scheme_id.text.strip() if scheme_id is not None and scheme_id.text else ""
            scheme_name_text = scheme_name.text.strip().upper() if scheme_name is not None and scheme_name.text else ""

            if scheme_id_text == "01" or "IVA" in scheme_name_text:
                if percent is not None and percent.text:
                    return self._parse_decimal(percent.text)

        # Si no hay IVA explicito, tomar el primer Percent > 0 en TaxSubtotal
        for tax_subtotal in line_element.findall('.//cac:TaxTotal/cac:TaxSubtotal', NAMESPACES):
            percent = tax_subtotal.find('.//cac:TaxCategory/cbc:Percent', NAMESPACES)
            if percent is not None and percent.text:
                valor = self._parse_decimal(percent.text)
                if valor > Decimal('0'):
                    return valor

        # Alternativa: buscar en AllowanceCharge
        iva_element = line_element.find('.//cac:AllowanceCharge/cac:TaxCategory/cbc:Percent', NAMESPACES)
        if iva_element is not None and iva_element.text:
            return self._parse_decimal(iva_element.text)

        # Alternativa: buscar cualquier TaxCategory/Percent dentro de la línea
        iva_element = line_element.find('.//cac:TaxCategory/cbc:Percent', NAMESPACES)
        if iva_element is not None and iva_element.text:
            return self._parse_decimal(iva_element.text)

        # Búsqueda amplia: primer Percent > 0 dentro de la línea
        for elem in line_element.iter():
            if elem.tag.endswith('Percent') and elem.text:
                valor = self._parse_decimal(elem.text)
                if valor > Decimal('0'):
                    return valor

        # Default: 19% (IVA común en Colombia)
        return Decimal('19')

    def _parse_decimal_texto(self, value: str) -> Optional[Decimal]:
        """Parsea un numero desde texto, retorna None si no es valido."""
        try:
            return Decimal(str(value).replace(',', '.'))
        except (InvalidOperation, ValueError, AttributeError):
            return None

    def _detectar_unidades_pack(self, nombre: str) -> int:
        """Detecta unidades por pack en el nombre del producto."""
        if 'SIXPACK' in nombre or re.search(r'\bSIX\b', nombre):
            return 6
        if 'FOURPACK' in nombre:
            return 4

        match = re.search(r'\bRISTRA\b.*?(\d+)\s*UND', nombre)
        if match:
            return int(match.group(1))

        match = re.search(r'\bDISPLAY\b.*?X\s*(\d+)', nombre)
        if match:
            return int(match.group(1))

        match = re.search(r'(?:PQ|PACK)\s*(\d+)', nombre)
        if match:
            return int(match.group(1))

        return 1

    def _extraer_volumen_y_pack(self, nombre: str, unidad_original: str) -> Tuple[Optional[Decimal], Optional[str], int]:
        """Extrae volumen/peso y unidades de pack desde el nombre."""
        patrones_combinados = [
            ('Lt', r'(\d+(?:[.,]\d+)?)\s*ML\s*X\s*(\d+)', False),
            ('Lt', r'(\d+)\s*X\s*(\d+(?:[.,]\d+)?)\s*ML', True),
            ('Kg', r'(\d+(?:[.,]\d+)?)\s*G[R]?\s*X\s*(\d+)', False),
            ('Kg', r'(\d+)\s*X\s*(\d+(?:[.,]\d+)?)\s*G[R]?', True),
            ('Kg', r'(\d+(?:[.,]\d+)?)\s*K[GL]\s*X\s*(\d+)', False),
            ('Kg', r'(\d+)\s*X\s*(\d+(?:[.,]\d+)?)\s*K[GL]', True),
            ('Lt', r'(\d+(?:[.,]\d+)?)\s*LITRO[S]?\s*X\s*(\d+)', False),
            ('Lt', r'(\d+)\s*X\s*(\d+(?:[.,]\d+)?)\s*LITRO[S]?', True),
        ]

        for unidad, patron, pack_first in patrones_combinados:
            match = re.search(patron, nombre)
            if match:
                if pack_first:
                    unidades_pack = int(match.group(1))
                    volumen_raw = self._parse_decimal_texto(match.group(2))
                else:
                    volumen_raw = self._parse_decimal_texto(match.group(1))
                    unidades_pack = int(match.group(2))

                if volumen_raw is None:
                    continue

                if unidad == 'Lt':
                    if 'ML' in patron:
                        volumen = volumen_raw / Decimal('1000')
                    else:
                        volumen = volumen_raw
                else:
                    if 'G' in patron and 'K' not in patron:
                        volumen = volumen_raw / Decimal('1000')
                    else:
                        volumen = volumen_raw

                return volumen, unidad, unidades_pack

        if unidad_original in ['KG']:
            patrones = [
                ('Kg', r'(?:\bX\s*)?(\d+(?:[.,]\d+)?)\s*K[GL]\b'),
                ('Kg', r'(\d+(?:[.,]\d+)?)\s*G[R]?\b'),
            ]
        else:
            patrones = [
                ('Lt', r'(?:\bX\s*)?(\d+(?:[.,]\d+)?)\s*ML\b'),
                ('Kg', r'(?:\bX\s*)?(\d+(?:[.,]\d+)?)\s*K[GL]\b'),
                ('Kg', r'(\d+(?:[.,]\d+)?)\s*G[R]?\b'),
                ('Lt', r'(\d+(?:[.,]\d+)?)\s*LITRO[S]?\b'),
            ]

        unidades_pack = self._detectar_unidades_pack(nombre)

        for unidad, patron in patrones:
            match = re.search(patron, nombre)
            if not match:
                continue
            valor = self._parse_decimal_texto(match.group(1))
            if valor is None:
                continue

            if unidad == 'Lt':
                volumen = valor / Decimal('1000') if 'ML' in patron else valor
            else:
                volumen = valor / Decimal('1000') if 'G' in patron and 'K' not in patron else valor

            return volumen, unidad, unidades_pack

        if unidad_original not in ['KG']:
            match = re.search(r'(?:\bX\s*)?(\d+(?:[.,]\d+)?)\s*(PARMA|PROLE|LATTI|EDGE|PROL)\b', nombre)
            if match:
                valor = self._parse_decimal_texto(match.group(1))
                if valor is not None:
                    volumen = valor / Decimal('1000') if valor > 100 else valor
                    return volumen, 'Lt', unidades_pack

            match = re.search(r'\bX\s*(\d+(?:[.,]\d+)?)\b', nombre)
            if match:
                valor = self._parse_decimal_texto(match.group(1))
                if valor is not None:
                    volumen = valor / Decimal('1000') if valor > 100 else valor
                    return volumen, 'Lt', unidades_pack

        return None, None, unidades_pack

    def _detectar_unidad_destino(self, nombre: str, unidad_original: str) -> str:
        """Determina unidad destino (Lt o Kg) por heuristica."""
        if any(x in nombre for x in ['CREMA', 'POLVO', 'GR', 'KG', 'KL']):
            return 'Kg'
        if any(x in nombre for x in ['LECHE', 'L.', 'UHT', 'ZYMIL']):
            return 'Lt'
        if unidad_original in ['KG', 'KGM', 'KG.']:
            return 'Kg'
        return 'Lt'

    def _convertir_cantidad_bmc(self, cantidad_original: Decimal, unidad_original: str, nombre_producto: str) -> Tuple[Decimal, str, Decimal, bool, str]:
        """Convierte la cantidad a Kg o Lt segun el nombre del producto."""
        nombre = (nombre_producto or '').upper()
        unidad_orig = (unidad_original or '').upper()

        volumen, unidad_volumen, unidades_pack = self._extraer_volumen_y_pack(nombre, unidad_orig)
        if volumen is None or unidad_volumen is None:
            unidad_destino = self._detectar_unidad_destino(nombre, unidad_orig)
            return cantidad_original, unidad_destino, Decimal('1'), False, 'No se pudo determinar volumen/peso'

        factor = volumen * Decimal(unidades_pack)
        cantidad_convertida = cantidad_original * factor
        unidad_destino = unidad_volumen

        return cantidad_convertida, unidad_destino, factor, True, ''

    def _parse_decimal(self, value: str) -> Decimal:
        """
        Parsea un string a Decimal de forma segura
        
        Args:
            value: String con número

        Returns:
            Decimal
        """
        try:
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
        formato = f"{{:.{decimales}f}}"
        numero_str = formato.format(numero)
        return numero_str.replace('.', ',')
