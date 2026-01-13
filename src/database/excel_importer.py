"""
Utilidad para importar materiales y clientes desde archivos Excel
Valida los encabezados y formatos antes de importar
"""

import pandas as pd
import logging
from typing import List, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ExcelImporterError(Exception):
    """Excepción para errores de importación de Excel"""
    pass


class ExcelImporter:
    """
    Importador de datos desde Excel para Lactalis Ventas

    ENCABEZADOS REQUERIDOS:
    - Materiales: CODIGO, DESCRIPCION, SOCIEDAD
    - Clientes: Cód.Padre, Nombre Código Padre, NIT
    """

    # Encabezados esperados
    MATERIALES_HEADERS = ['CODIGO', 'DESCRIPCION', 'SOCIEDAD']
    CLIENTES_HEADERS = ['Cód.Padre', 'Nombre Código Padre', 'NIT']

    # Mapeo de variantes de encabezados (normalización)
    MATERIALES_HEADERS_VARIANTS = {
        'codigo': 'CODIGO',
        'código': 'CODIGO',
        'code': 'CODIGO',
        'descripcion': 'DESCRIPCION',
        'descripción': 'DESCRIPCION',
        'description': 'DESCRIPCION',
        'sociedad': 'SOCIEDAD',
        'company': 'SOCIEDAD'
    }

    CLIENTES_HEADERS_VARIANTS = {
        'cod.padre': 'Cód.Padre',
        'cod padre': 'Cód.Padre',
        'codigo padre': 'Cód.Padre',
        'código padre': 'Cód.Padre',
        'nombre codigo padre': 'Nombre Código Padre',
        'nombre código padre': 'Nombre Código Padre',
        'nombre': 'Nombre Código Padre',
        'nit': 'NIT'
    }

    @staticmethod
    def importar_materiales_desde_excel(archivo_path: str) -> List[Dict]:
        """
        Importa materiales desde un archivo Excel

        Args:
            archivo_path: Ruta al archivo Excel

        Returns:
            Lista de diccionarios con materiales

        Raises:
            ExcelImporterError: Si hay problemas con el archivo o formato
        """
        try:
            # Verificar que el archivo existe
            if not Path(archivo_path).exists():
                raise ExcelImporterError(f"Archivo no encontrado: {archivo_path}")

            # Leer el archivo Excel
            logger.info(f"Leyendo archivo de materiales: {archivo_path}")
            df = pd.read_excel(archivo_path, sheet_name=0)

            # Validar que no esté vacío
            if df.empty:
                raise ExcelImporterError("El archivo está vacío")

            # Normalizar nombres de columnas (eliminar espacios, convertir a mayúsculas)
            df.columns = df.columns.str.strip()

            # Validar encabezados
            headers_originales = df.columns.tolist()
            logger.debug(f"Encabezados encontrados: {headers_originales}")

            # Intentar mapear encabezados con variantes
            df_renamed = df.copy()
            columnas_mapeadas = {}

            for col in df_renamed.columns:
                col_lower = col.lower().strip()
                if col_lower in ExcelImporter.MATERIALES_HEADERS_VARIANTS:
                    columnas_mapeadas[col] = ExcelImporter.MATERIALES_HEADERS_VARIANTS[col_lower]

            if columnas_mapeadas:
                df_renamed.rename(columns=columnas_mapeadas, inplace=True)
                logger.info(f"Columnas normalizadas: {columnas_mapeadas}")

            # Verificar que todos los encabezados requeridos estén presentes
            headers_actuales = df_renamed.columns.tolist()
            headers_faltantes = [h for h in ExcelImporter.MATERIALES_HEADERS if h not in headers_actuales]

            if headers_faltantes:
                raise ExcelImporterError(
                    f"Encabezados faltantes: {headers_faltantes}. "
                    f"Se esperan: {ExcelImporter.MATERIALES_HEADERS}"
                )

            # Convertir a lista de diccionarios
            materiales = []
            for idx, row in df_renamed.iterrows():
                material = {
                    'codigo': str(row['CODIGO']).strip() if pd.notna(row['CODIGO']) else '',
                    'descripcion': str(row['DESCRIPCION']).strip() if pd.notna(row['DESCRIPCION']) else '',
                    'sociedad': str(row['SOCIEDAD']).strip() if pd.notna(row['SOCIEDAD']) else ''
                }

                # Filtrar filas vacías
                if material['codigo'] or material['descripcion'] or material['sociedad']:
                    materiales.append(material)

            logger.info(f"Materiales extraídos: {len(materiales)}")
            return materiales

        except pd.errors.EmptyDataError:
            raise ExcelImporterError("El archivo está vacío o no se pudo leer")
        except Exception as e:
            logger.error(f"Error importando materiales: {str(e)}")
            raise ExcelImporterError(f"Error leyendo archivo: {str(e)}")

    @staticmethod
    def importar_clientes_desde_excel(archivo_path: str) -> List[Dict]:
        """
        Importa clientes desde un archivo Excel

        Args:
            archivo_path: Ruta al archivo Excel

        Returns:
            Lista de diccionarios con clientes

        Raises:
            ExcelImporterError: Si hay problemas con el archivo o formato
        """
        try:
            # Verificar que el archivo existe
            if not Path(archivo_path).exists():
                raise ExcelImporterError(f"Archivo no encontrado: {archivo_path}")

            # Leer el archivo Excel
            logger.info(f"Leyendo archivo de clientes: {archivo_path}")
            df = pd.read_excel(archivo_path, sheet_name=0)

            # Validar que no esté vacío
            if df.empty:
                raise ExcelImporterError("El archivo está vacío")

            # Normalizar nombres de columnas
            df.columns = df.columns.str.strip()

            # Validar encabezados
            headers_originales = df.columns.tolist()
            logger.debug(f"Encabezados encontrados: {headers_originales}")

            # Intentar mapear encabezados con variantes
            df_renamed = df.copy()
            columnas_mapeadas = {}

            for col in df_renamed.columns:
                col_lower = col.lower().strip()
                if col_lower in ExcelImporter.CLIENTES_HEADERS_VARIANTS:
                    columnas_mapeadas[col] = ExcelImporter.CLIENTES_HEADERS_VARIANTS[col_lower]

            if columnas_mapeadas:
                df_renamed.rename(columns=columnas_mapeadas, inplace=True)
                logger.info(f"Columnas normalizadas: {columnas_mapeadas}")

            # Verificar que todos los encabezados requeridos estén presentes
            headers_actuales = df_renamed.columns.tolist()
            headers_faltantes = [h for h in ExcelImporter.CLIENTES_HEADERS if h not in headers_actuales]

            if headers_faltantes:
                raise ExcelImporterError(
                    f"Encabezados faltantes: {headers_faltantes}. "
                    f"Se esperan: {ExcelImporter.CLIENTES_HEADERS}"
                )

            # Convertir a lista de diccionarios
            clientes = []
            for idx, row in df_renamed.iterrows():
                cliente = {
                    'cod_padre': str(row['Cód.Padre']).strip() if pd.notna(row['Cód.Padre']) else '',
                    'nombre_codigo_padre': str(row['Nombre Código Padre']).strip() if pd.notna(row['Nombre Código Padre']) else '',
                    'nit': str(row['NIT']).strip() if pd.notna(row['NIT']) else ''
                }

                # Filtrar filas vacías
                if cliente['cod_padre'] or cliente['nombre_codigo_padre']:
                    clientes.append(cliente)

            logger.info(f"Clientes extraídos: {len(clientes)}")
            return clientes

        except pd.errors.EmptyDataError:
            raise ExcelImporterError("El archivo está vacío o no se pudo leer")
        except Exception as e:
            logger.error(f"Error importando clientes: {str(e)}")
            raise ExcelImporterError(f"Error leyendo archivo: {str(e)}")

    @staticmethod
    def validar_archivo_materiales(archivo_path: str) -> Tuple[bool, str]:
        """
        Valida que un archivo Excel tenga el formato correcto para materiales

        Args:
            archivo_path: Ruta al archivo Excel

        Returns:
            Tupla (es_valido, mensaje)
        """
        try:
            if not Path(archivo_path).exists():
                return False, f"Archivo no encontrado: {archivo_path}"

            df = pd.read_excel(archivo_path, sheet_name=0, nrows=0)
            df.columns = df.columns.str.strip()

            # Intentar mapear encabezados
            columnas_mapeadas = {}
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in ExcelImporter.MATERIALES_HEADERS_VARIANTS:
                    columnas_mapeadas[col] = ExcelImporter.MATERIALES_HEADERS_VARIANTS[col_lower]

            headers_actuales = [columnas_mapeadas.get(col, col) for col in df.columns]
            headers_faltantes = [h for h in ExcelImporter.MATERIALES_HEADERS if h not in headers_actuales]

            if headers_faltantes:
                return False, f"Encabezados faltantes: {', '.join(headers_faltantes)}"

            return True, "Formato válido"

        except Exception as e:
            return False, f"Error validando archivo: {str(e)}"

    @staticmethod
    def validar_archivo_clientes(archivo_path: str) -> Tuple[bool, str]:
        """
        Valida que un archivo Excel tenga el formato correcto para clientes

        Args:
            archivo_path: Ruta al archivo Excel

        Returns:
            Tupla (es_valido, mensaje)
        """
        try:
            if not Path(archivo_path).exists():
                return False, f"Archivo no encontrado: {archivo_path}"

            df = pd.read_excel(archivo_path, sheet_name=0, nrows=0)
            df.columns = df.columns.str.strip()

            # Intentar mapear encabezados
            columnas_mapeadas = {}
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in ExcelImporter.CLIENTES_HEADERS_VARIANTS:
                    columnas_mapeadas[col] = ExcelImporter.CLIENTES_HEADERS_VARIANTS[col_lower]

            headers_actuales = [columnas_mapeadas.get(col, col) for col in df.columns]
            headers_faltantes = [h for h in ExcelImporter.CLIENTES_HEADERS if h not in headers_actuales]

            if headers_faltantes:
                return False, f"Encabezados faltantes: {', '.join(headers_faltantes)}"

            return True, "Formato válido"

        except Exception as e:
            return False, f"Error validando archivo: {str(e)}"
