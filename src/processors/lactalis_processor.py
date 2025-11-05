"""
Procesador específico para LACTALIS COMPRAS
Maneja ZIPs que pueden contener otros ZIPs o XMLs directamente
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import logging
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from config.constants import REGGIS_HEADERS
from extractors.lactalis_extractor import FacturaExtractorLactalis

logger = logging.getLogger(__name__)


class ProcesadorLactalisCompras:
    """Procesador específico para LACTALIS COMPRAS"""

    def __init__(self, carpeta_zip: Path, carpeta_salida: Path):
        self.carpeta_zip = carpeta_zip
        self.carpeta_salida = carpeta_salida
        self.processed_lines = []
        self.archivos_procesados = 0
        self.temp_dir = None

    def extract_all_xmls_from_zip(self, zip_path: Path, extract_to: Path) -> List[Path]:
        """
        Extrae recursivamente todos los XMLs de un ZIP
        que puede contener otros ZIPs o XMLs directamente
        """
        xml_files = []

        try:
            logger.info(f"Extrayendo: {zip_path.name}")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extraer todo el contenido
                zip_ref.extractall(extract_to)

            # Buscar XMLs y ZIPs en el directorio extraído
            for item in extract_to.rglob('*'):
                if item.is_file():
                    if item.suffix.lower() == '.xml':
                        # Es un XML, agregarlo
                        xml_files.append(item)
                        logger.info(f"  XML encontrado: {item.name}")

                    elif item.suffix.lower() == '.zip':
                        # Es otro ZIP, extraer recursivamente
                        logger.info(f"  ZIP anidado encontrado: {item.name}")
                        nested_extract = extract_to / f"nested_{item.stem}"
                        nested_extract.mkdir(exist_ok=True)
                        nested_xmls = self.extract_all_xmls_from_zip(item, nested_extract)
                        xml_files.extend(nested_xmls)

        except Exception as e:
            logger.error(f"Error al extraer {zip_path.name}: {str(e)}")

        return xml_files

    def process_xml_file(self, xml_path: Path) -> List[Dict]:
        """Procesa un archivo XML individual"""
        try:
            logger.info(f"Procesando XML: {xml_path.name}")

            # Leer el contenido del XML
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()

            # Usar el extractor de Lactalis
            extractor = FacturaExtractorLactalis(xml_content)
            lines = extractor.extraer_datos()

            if lines:
                logger.info(f"  Extraídas {len(lines)} líneas de {xml_path.name}")
            else:
                logger.warning(f"  No se extrajeron líneas de {xml_path.name}")

            return lines

        except Exception as e:
            logger.error(f"Error procesando {xml_path.name}: {str(e)}")
            return []

    def create_reggis_excel(self, output_path: Path):
        """Crea el archivo Excel con formato REGGIS"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Facturas Lactalis"

        # Encabezados
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")

        for col, header in enumerate(REGGIS_HEADERS, start=1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Datos
        for idx, line in enumerate(self.processed_lines, start=2):
            row_data = [
                line['numero_factura'],
                line['nombre_producto'],
                line['codigo_subyacente'],
                line['unidad_medida'],
                line['cantidad'],
                line['precio_unitario'],
                line['fecha_factura'],
                line['fecha_pago'],
                line['nit_comprador'],
                line['nombre_comprador'],
                line['nit_vendedor'],
                line['nombre_vendedor'],
                line['principal'],
                line['municipio'],
                line['iva'],
                line['descripcion'],
                line['activa_factura'],
                line['activa_bodega'],
                line['incentivo'],
                line['cantidad_original'],
                line['moneda'],
                round(line['total_sin_iva'], 2),
                round(line['total_iva'], 2),
                round(line['total_con_iva'], 2)
            ]

            for col, value in enumerate(row_data, start=1):
                cell = ws.cell(row=idx, column=col, value=value)
                cell.alignment = Alignment(vertical='center')

        # Ajustar anchos de columna
        column_widths = [15, 40, 15, 20, 15, 15, 12, 12, 15, 30, 15, 30, 12, 20, 8, 50, 12, 12, 10, 18, 10, 15, 12, 15]
        for col, width in enumerate(column_widths, start=1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width

        wb.save(output_path)
        logger.info(f"Excel REGGIS creado: {output_path}")

    def procesar(self) -> Path:
        """Ejecuta el procesamiento completo"""
        try:
            # Buscar archivos ZIP en la carpeta
            zip_files = list(self.carpeta_zip.glob("*.zip"))

            if not zip_files:
                logger.warning("No se encontraron archivos ZIP en la carpeta seleccionada")
                # Buscar XMLs directamente
                xml_files = list(self.carpeta_zip.glob("*.xml"))
                if xml_files:
                    logger.info(f"Lactalis: Encontrados {len(xml_files)} archivos XML directos")
                    for xml_file in xml_files:
                        lines = self.process_xml_file(xml_file)
                        self.processed_lines.extend(lines)
                        if lines:
                            self.archivos_procesados += 1
                else:
                    raise Exception("No se encontraron archivos ZIP ni XML en la carpeta seleccionada")
            else:
                logger.info(f"Lactalis: Encontrados {len(zip_files)} archivos ZIP")

                # Crear directorio temporal para extracciones
                self.temp_dir = Path(tempfile.gettempdir()) / f"lactalis_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.temp_dir.mkdir(exist_ok=True)

                # Procesar cada ZIP
                for zip_file in zip_files:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Procesando ZIP principal: {zip_file.name}")
                    logger.info(f"{'='*60}")

                    # Crear subdirectorio para este ZIP
                    extract_dir = self.temp_dir / zip_file.stem
                    extract_dir.mkdir(exist_ok=True)

                    # Extraer todos los XMLs (incluyendo ZIPs anidados)
                    xml_files = self.extract_all_xmls_from_zip(zip_file, extract_dir)

                    logger.info(f"\nTotal de XMLs encontrados en {zip_file.name}: {len(xml_files)}")

                    # Procesar cada XML
                    for xml_file in xml_files:
                        lines = self.process_xml_file(xml_file)
                        if lines:
                            self.processed_lines.extend(lines)
                            self.archivos_procesados += 1

            if not self.processed_lines:
                raise Exception("No se procesaron líneas. Verifique los archivos.")

            logger.info(f"\n{'='*60}")
            logger.info(f"Resumen Lactalis Compras:")
            logger.info(f"  Archivos procesados: {self.archivos_procesados}")
            logger.info(f"  Líneas totales: {len(self.processed_lines)}")
            logger.info(f"{'='*60}")

            # Crear el Excel de salida
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.carpeta_salida / f"Facturas_REGGIS_LACTALIS_{timestamp}.xlsx"

            self.create_reggis_excel(output_file)

            logger.info(f"Lactalis: Proceso completado exitosamente")

            return self.carpeta_salida

        finally:
            # Limpiar directorio temporal
            if self.temp_dir and self.temp_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(self.temp_dir)
                    logger.info("Archivos temporales eliminados")
                except Exception as e:
                    logger.warning(f"No se pudieron eliminar archivos temporales: {e}")
