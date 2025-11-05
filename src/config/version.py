"""
Control de versiones de la aplicación
"""

# Versión actual de la aplicación
__version__ = "1.0.0"

# Información de la aplicación
APP_NAME = "Procesador de Facturas REGGIS"
APP_AUTHOR = "CORREAGRO S.A"
APP_DESCRIPTION = "Sistema unificado de procesamiento de facturas electrónicas"

# URL del repositorio para actualizaciones
GITHUB_REPO = "InteligenciaCorreagro/bogota-sae"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# Configuración de actualización
AUTO_UPDATE_ENABLED = True
CHECK_UPDATE_ON_STARTUP = True
UPDATE_CHECK_INTERVAL_HOURS = 24
