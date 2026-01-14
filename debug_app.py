"""
Script de debugging para lanzar la aplicación con logging máximo
Ejecutar con: python3 debug_app.py
"""

import sys
import logging
from pathlib import Path

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configurar logging ANTES de cualquier import
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug_app.log', mode='w', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("INICIANDO APLICACIÓN EN MODO DEBUG")
logger.info("=" * 80)

try:
    logger.info("Importando PyQt6...")
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    logger.info("✅ PyQt6 importado")

    logger.info("Importando módulo principal...")
    from ui.main_window import MainWindow
    logger.info("✅ MainWindow importado")

    logger.info("Creando aplicación Qt...")
    app = QApplication(sys.argv)
    logger.info("✅ QApplication creada")

    logger.info("Creando ventana principal...")
    window = MainWindow()
    logger.info("✅ MainWindow creada")

    logger.info("Mostrando ventana...")
    window.show()
    logger.info("✅ Ventana mostrada")

    logger.info("Iniciando event loop...")
    sys.exit(app.exec())

except Exception as e:
    logger.error("=" * 80)
    logger.error("❌ ERROR FATAL AL INICIAR LA APLICACIÓN")
    logger.error("=" * 80)
    logger.error(f"Tipo de error: {type(e).__name__}")
    logger.error(f"Mensaje: {str(e)}")
    logger.error("Stack trace completo:", exc_info=True)
    logger.error("=" * 80)
    sys.exit(1)
