"""
Constantes y configuración para el procesador de facturas
"""

import os
from pathlib import Path
from datetime import datetime

# Namespaces UBL estándar para Colombia
NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
}

# Mapeo de códigos de moneda
CURRENCY_CODE_MAP = {
    'COP': '1',
    'USD': '2',
    'EUR': '3'
}

# Mapeo de unidades de medida
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

# Encabezados de Excel para formato REGGIS
REGGIS_HEADERS = [
    'N° Factura',
    'Nombre Producto',
    'Codigo Subyacente',
    'Unidad Medida en Kg,Un,Lt',
    'Cantidad (5 decimales - separdor coma)',
    'Precio Unitario (5 decimales - separdor coma)',
    'Fecha Factura Año-Mes-Dia',
    'Fecha Pago Año-Mes-Dia',
    'Nit Comprador (Existente)',
    'Nombre Comprador',
    'Nit Vendedor (Existente)',
    'Nombre Vendedor',
    'Principal V,C',
    'Municipio (Nombre Exacto de la Ciudad)',
    'Iva (N°%)',
    'Descripción',
    'Activa Factura',
    'Activa Bodega',
    'Incentivo',
    'Cantidad Original (5 decimales - separdor coma)',
    'Moneda (1,2,3)',
    'Total Sin IVA',
    'Total IVA',
    'Total Con IVA'
]

# Constantes específicas para LACTALIS COMPRAS
LACTALIS_CONFIG = {
    # NIT de Lactalis (comprador) - CONFIGURAR CON EL NIT REAL
    'nit_comprador': '890800458',  # TODO: Verificar NIT correcto de Lactalis
    'nombre_comprador': 'LACTALIS',

    # Valores fijos para todas las líneas
    'codigo_subyacente': 'SPN-1',
    'nombre_producto': 'LECHE CRUDA',
    'unidad_medida': 'Lt',
    'activa_factura': '1',
    'activa_bodega': '1',
    'descripcion': '',
    'principal': 'C',  # Lactalis como Comprador
}


def get_app_data_dir() -> Path:
    """
    Retorna el directorio base para datos de la aplicación según el sistema operativo.
    En Windows usa APPDATA para evitar problemas de permisos en Program Files.

    Returns:
        Path al directorio base de datos de la aplicación
    """
    if os.name == 'nt':  # Windows
        # Usar APPDATA en Windows para tener permisos de escritura
        appdata = Path(os.environ.get('APPDATA', '.'))
        app_dir = appdata / 'BogotaSAE'
    else:
        # En otros sistemas, usar directorio actual
        app_dir = Path('.')

    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_logs_dir() -> Path:
    """
    Retorna el directorio para logs de la aplicación.

    Returns:
        Path al directorio de logs
    """
    if os.name == 'nt':  # Windows
        logs_dir = get_app_data_dir() / 'logs'
    else:
        logs_dir = Path('logs')

    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_data_dir() -> Path:
    """
    Retorna el directorio base para archivos procesados.

    Returns:
        Path al directorio de datos
    """
    if os.name == 'nt':  # Windows
        data_dir = get_app_data_dir() / 'data'
    else:
        data_dir = Path('data')

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_data_output_path(subfolder: str = "") -> Path:
    """
    Crea y retorna la ruta de salida para archivos procesados.
    Estructura: data/YYYY-MM-DD/subfolder/

    Args:
        subfolder: Subcarpeta opcional dentro de la fecha

    Returns:
        Path a la carpeta de salida
    """
    # Carpeta base de datos (usa la función helper para ubicación correcta)
    data_dir = get_data_dir()

    # Carpeta con fecha de hoy
    today = datetime.now().strftime('%Y-%m-%d')
    date_dir = data_dir / today
    date_dir.mkdir(exist_ok=True)

    # Si hay subcarpeta, crearla
    if subfolder:
        output_dir = date_dir / subfolder
        output_dir.mkdir(exist_ok=True)
        return output_dir

    return date_dir
