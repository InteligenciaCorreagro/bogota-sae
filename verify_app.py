"""
Script de verificación rápida sin GUI
Verifica que todos los imports y la estructura básica funcionen
"""

import sys
import os
import logging
from pathlib import Path

# Configurar Qt para modo headless (sin display)
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Agregar el directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("VERIFICANDO ESTRUCTURA DE LA APLICACIÓN")
logger.info("=" * 60)

try:
    # Verificar imports de PyQt6
    logger.info("Importando PyQt6...")
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    logger.info("✅ PyQt6 importado correctamente")

    # Verificar imports de configuración
    logger.info("Importando config...")
    from config.logging_config import setup_logging
    from core.version import get_version_string
    logger.info("✅ Config importado correctamente")
    logger.info(f"   Versión: {get_version_string()}")

    # Verificar import de MainWindow
    logger.info("Importando MainWindow...")
    from ui.main_window import MainWindow
    logger.info("✅ MainWindow importado correctamente")

    # Verificar imports de database
    logger.info("Importando database...")
    from database.lactalis_database import LactalisDatabase
    from database.excel_importer import ExcelImporter
    logger.info("✅ Database importado correctamente")

    # Verificar imports de processors
    logger.info("Importando processors...")
    from processors.lactalis_ventas_processor import ProcesadorLactalisVentas
    logger.info("✅ Processors importado correctamente")

    # Verificar imports de tabs
    logger.info("Importando tabs...")
    from ui.tabs.tab_lactalis_ventas import TabLactalisVentas
    logger.info("✅ Tabs importado correctamente")

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ VERIFICACIÓN EXITOSA")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Todos los componentes se importan correctamente.")
    logger.info("La aplicación está lista para ser ejecutada con:")
    logger.info("  python3 app.py")
    logger.info("")

    sys.exit(0)

except Exception as e:
    logger.error("")
    logger.error("=" * 60)
    logger.error("❌ ERROR EN VERIFICACIÓN")
    logger.error("=" * 60)
    logger.error(f"Tipo: {type(e).__name__}")
    logger.error(f"Mensaje: {str(e)}")
    logger.error("")
    logger.error("Stack trace:", exc_info=True)
    sys.exit(1)
