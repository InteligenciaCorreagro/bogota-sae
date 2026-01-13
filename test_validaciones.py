"""
Script de prueba para validar el funcionamiento de la base de datos
y las validaciones de materiales y clientes
"""

import sys
import logging
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.database.lactalis_database import LactalisDatabase

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database():
    """Prueba básica de la base de datos"""
    logger.info("=" * 60)
    logger.info("INICIANDO PRUEBAS DE BASE DE DATOS")
    logger.info("=" * 60)

    # Crear instancia de base de datos
    db = LactalisDatabase()

    logger.info(f"Base de datos ubicada en: {db.db_path}")
    logger.info(f"Total materiales: {db.contar_materiales()}")
    logger.info(f"Total clientes: {db.contar_clientes()}")

    # Listar algunos materiales
    logger.info("\n" + "=" * 60)
    logger.info("MATERIALES EN BD (primeros 10):")
    logger.info("=" * 60)
    materiales = db.listar_materiales(limit=10)
    for mat in materiales:
        logger.info(f"  - Código: {mat['codigo']}, Descripción: {mat['descripcion']}, Sociedad: {mat['sociedad']}")

    # Listar algunos clientes
    logger.info("\n" + "=" * 60)
    logger.info("CLIENTES EN BD (primeros 10):")
    logger.info("=" * 60)
    clientes = db.listar_clientes(limit=10)
    for cli in clientes:
        logger.info(f"  - Cód.Padre: {cli['cod_padre']}, Nombre: {cli['nombre_codigo_padre']}, NIT: {cli['nit']}")

    # Prueba de validación de material
    logger.info("\n" + "=" * 60)
    logger.info("PRUEBAS DE VALIDACIÓN DE MATERIALES:")
    logger.info("=" * 60)

    if materiales:
        # Probar con un material que existe
        mat = materiales[0]
        codigo = mat['codigo']
        sociedad = mat['sociedad']
        existe = db.validar_material(codigo, sociedad)
        logger.info(f"Material {codigo} + Sociedad {sociedad}: {'✅ EXISTE' if existe else '❌ NO EXISTE'}")

        # Probar con un material que NO existe
        existe = db.validar_material("CODIGO_INEXISTENTE", "800245795")
        logger.info(f"Material CODIGO_INEXISTENTE + Sociedad 800245795: {'✅ EXISTE' if existe else '❌ NO EXISTE'}")

    # Prueba de validación de cliente
    logger.info("\n" + "=" * 60)
    logger.info("PRUEBAS DE VALIDACIÓN DE CLIENTES (POR NIT):")
    logger.info("=" * 60)

    if clientes:
        # Probar con un cliente que existe (validar por NIT)
        cli = clientes[0]
        if cli['nit']:
            nit = cli['nit']
            existe = db.validar_cliente(nit)
            logger.info(f"Cliente con NIT {nit}: {'✅ EXISTE' if existe else '❌ NO EXISTE'}")
        else:
            logger.info(f"Cliente {cli['cod_padre']} no tiene NIT registrado")

        # Probar con un cliente que NO existe
        existe = db.validar_cliente("999999999")
        logger.info(f"Cliente con NIT 999999999: {'✅ EXISTE' if existe else '❌ NO EXISTE'}")

    logger.info("\n" + "=" * 60)
    logger.info("PRUEBAS COMPLETADAS")
    logger.info("=" * 60)

    db.cerrar()

if __name__ == "__main__":
    test_database()
