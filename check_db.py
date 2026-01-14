#!/usr/bin/env python3
"""
Script para verificar el contenido de la base de datos
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.lactalis_database import LactalisDatabase

print("=" * 60)
print("VERIFICANDO BASE DE DATOS")
print("=" * 60)

try:
    db = LactalisDatabase()
    print(f"\n✅ Base de datos conectada: {db.db_path}")

    # Contar registros
    num_materiales = db.contar_materiales()
    num_clientes = db.contar_clientes()

    print(f"\n📊 REGISTROS EN BASE DE DATOS:")
    print(f"  • Materiales: {num_materiales}")
    print(f"  • Clientes: {num_clientes}")

    if num_materiales == 0:
        print("\n⚠️  NO HAY MATERIALES EN LA BASE DE DATOS")
        print("   Debes importar materiales desde Excel antes de procesar")
    else:
        print(f"\n✅ Hay {num_materiales} materiales en la BD")
        # Mostrar algunos ejemplos
        cursor = db.conn.cursor()
        cursor.execute("SELECT codigo, descripcion, sociedad FROM materiales LIMIT 5")
        print("\n   Ejemplos:")
        for row in cursor.fetchall():
            print(f"     - {row[0]} | {row[1][:50]} | {row[2]}")

    if num_clientes == 0:
        print("\n⚠️  NO HAY CLIENTES EN LA BASE DE DATOS")
        print("   Debes importar clientes desde Excel antes de procesar")
    else:
        print(f"\n✅ Hay {num_clientes} clientes en la BD")
        # Mostrar algunos ejemplos
        cursor = db.conn.cursor()
        cursor.execute("SELECT cod_padre, nombre_codigo_padre, nit FROM clientes LIMIT 5")
        print("\n   Ejemplos:")
        for row in cursor.fetchall():
            print(f"     - {row[0]} | {row[1][:50]} | {row[2]}")

    db.cerrar()
    print("\n" + "=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
