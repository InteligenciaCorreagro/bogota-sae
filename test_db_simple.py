"""
Script de prueba simple para verificar la base de datos
Ejecutar con: python3 test_db_simple.py
"""

import sys
import logging
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Configurar logging para ver TODOS los mensajes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_imports():
    """Prueba que todos los imports funcionen"""
    logger.info("=" * 60)
    logger.info("PASO 1: Probando imports...")
    logger.info("=" * 60)

    try:
        logger.info("Importando openpyxl...")
        import openpyxl
        logger.info("✅ openpyxl importado correctamente")
    except Exception as e:
        logger.error(f"❌ Error importando openpyxl: {str(e)}")
        return False

    try:
        logger.info("Importando sqlite3...")
        import sqlite3
        logger.info("✅ sqlite3 importado correctamente")
    except Exception as e:
        logger.error(f"❌ Error importando sqlite3: {str(e)}")
        return False

    try:
        logger.info("Importando LactalisDatabase...")
        from src.database.lactalis_database import LactalisDatabase
        logger.info("✅ LactalisDatabase importado correctamente")
    except Exception as e:
        logger.error(f"❌ Error importando LactalisDatabase: {str(e)}", exc_info=True)
        return False

    try:
        logger.info("Importando ExcelImporter...")
        from src.database.excel_importer import ExcelImporter
        logger.info("✅ ExcelImporter importado correctamente")
    except Exception as e:
        logger.error(f"❌ Error importando ExcelImporter: {str(e)}", exc_info=True)
        return False

    return True

def test_database():
    """Prueba la creación y uso de la base de datos"""
    logger.info("\n" + "=" * 60)
    logger.info("PASO 2: Probando base de datos...")
    logger.info("=" * 60)

    try:
        from src.database.lactalis_database import LactalisDatabase

        logger.info("Creando instancia de base de datos...")
        db = LactalisDatabase()
        logger.info(f"✅ Base de datos creada en: {db.db_path}")

        logger.info("Contando materiales...")
        count_mat = db.contar_materiales()
        logger.info(f"✅ Materiales en BD: {count_mat}")

        logger.info("Contando clientes...")
        count_cli = db.contar_clientes()
        logger.info(f"✅ Clientes en BD: {count_cli}")

        logger.info("Cerrando base de datos...")
        db.cerrar()
        logger.info("✅ Base de datos cerrada correctamente")

        return True

    except Exception as e:
        logger.error(f"❌ Error con base de datos: {str(e)}", exc_info=True)
        return False

def test_excel_importer():
    """Prueba el importador de Excel"""
    logger.info("\n" + "=" * 60)
    logger.info("PASO 3: Probando ExcelImporter...")
    logger.info("=" * 60)

    try:
        from src.database.excel_importer import ExcelImporter

        logger.info("✅ ExcelImporter listo para usar")
        logger.info(f"   Encabezados materiales: {ExcelImporter.MATERIALES_HEADERS}")
        logger.info(f"   Encabezados clientes: {ExcelImporter.CLIENTES_HEADERS}")

        return True

    except Exception as e:
        logger.error(f"❌ Error con ExcelImporter: {str(e)}", exc_info=True)
        return False

def main():
    """Función principal"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 10 + "TEST DE BASE DE DATOS - LACTALIS VENTAS" + " " * 9 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")

    # Ejecutar pruebas
    paso1 = test_imports()
    if not paso1:
        logger.error("\n❌ FALLO EN PASO 1: Imports")
        return False

    paso2 = test_database()
    if not paso2:
        logger.error("\n❌ FALLO EN PASO 2: Base de datos")
        return False

    paso3 = test_excel_importer()
    if not paso3:
        logger.error("\n❌ FALLO EN PASO 3: ExcelImporter")
        return False

    # Resumen
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 18 + "✅ TODAS LAS PRUEBAS PASARON" + " " * 13 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ ERROR FATAL: {str(e)}", exc_info=True)
        sys.exit(1)
