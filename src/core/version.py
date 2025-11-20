"""
Información de versión de la aplicación
Sistema de control de versiones centralizado
"""

__version__ = "2.0.0"
APP_NAME = "Procesador de Facturas Electrónicas REGGIS"
BUILD_DATE = "2025-11-20"

# Información detallada de versión
VERSION_INFO = {
    'version': __version__,
    'app_name': APP_NAME,
    'build_date': BUILD_DATE,
    'author': 'Sistema REGGIS',
    'description': 'Procesador unificado de facturas XML a formato Excel REGGIS',

    # Configuración de auto-actualización
    # NOTA: Configurar estas URLs cuando esté listo para publicar actualizaciones
    'update_check_url': None,  # Deshabilitado hasta configurar URL válida
    'download_url_base': 'https://github.com/InteligenciaCorreagro/bogota-sae/releases/download',

    # Clientes soportados
    'supported_clients': [
        'SEABOARD',
        'CASA_DEL_AGRICULTOR',
        'LACTALIS_COMPRAS'
    ]
}


def get_version_string() -> str:
    """Retorna la versión en formato legible"""
    return f"{APP_NAME} v{__version__}"


def get_full_version_info() -> dict:
    """Retorna información completa de la versión"""
    return VERSION_INFO.copy()
