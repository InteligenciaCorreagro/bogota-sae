#!/usr/bin/env python
"""
Script para crear el ejecutable de la aplicación con PyInstaller
Ejecutar desde la raíz del proyecto: python build_exe.py
"""

import PyInstaller.__main__
import shutil
from pathlib import Path
import sys

# Importar versión
sys.path.insert(0, str(Path(__file__).parent / "src"))
from config.version import __version__, APP_NAME

def build_executable():
    """Construye el ejecutable usando PyInstaller"""

    print(f"🔨 Construyendo {APP_NAME} v{__version__}")
    print("=" * 60)

    # Limpiar directorios anteriores
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"🧹 Limpiando {dir_name}/")
            shutil.rmtree(dir_path)

    # Nombre del ejecutable
    exe_name = f"ProcesadorFacturas_v{__version__}"

    # Opciones de PyInstaller
    pyinstaller_args = [
        'run.py',                          # Script principal
        '--name', exe_name,                # Nombre del ejecutable
        '--onefile',                       # Un solo archivo
        '--windowed',                      # Sin ventana de consola
        '--icon', 'NONE',                  # Sin icono (agregar si existe)
        '--add-data', 'src;src',          # Incluir carpeta src
        '--hidden-import', 'PyQt6',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'requests',
        '--hidden-import', 'packaging',
        '--collect-all', 'PyQt6',
        '--clean',                         # Limpiar caché
        '--noconfirm',                     # No pedir confirmación
        f'--distpath=dist',                # Carpeta de salida
        f'--workpath=build',               # Carpeta de trabajo
    ]

    print("\n📦 Ejecutando PyInstaller...")
    print(f"   Nombre: {exe_name}.exe")
    print(f"   Versión: {__version__}")
    print()

    try:
        PyInstaller.__main__.run(pyinstaller_args)

        print("\n" + "=" * 60)
        print(f"✅ ¡Ejecutable creado exitosamente!")
        print(f"📍 Ubicación: dist/{exe_name}.exe")
        print(f"📊 Tamaño: {(Path('dist') / f'{exe_name}.exe').stat().st_size / (1024*1024):.1f} MB")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error al crear el ejecutable: {e}")
        return False


if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
