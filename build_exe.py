#!/usr/bin/env python
"""
Script para crear el ejecutable de la aplicación con PyInstaller
Ejecutar desde la raíz del proyecto: python build_exe.py
"""

import PyInstaller.__main__
import shutil
from pathlib import Path
import sys
import time

# Importar versión
sys.path.insert(0, str(Path(__file__).parent / "src"))
from config.version import __version__, APP_NAME

def safe_rmtree(path, max_retries=3, delay=1):
    """
    Elimina un directorio de forma segura con reintentos.

    Args:
        path: Ruta del directorio a eliminar
        max_retries: Número máximo de reintentos
        delay: Tiempo de espera entre reintentos (segundos)
    """
    for attempt in range(max_retries):
        try:
            if path.exists():
                shutil.rmtree(path, ignore_errors=False)
                return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"   [WARNING] Archivo en uso, reintentando en {delay}s... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                print(f"   [WARNING] No se pudo eliminar {path}: {e}")
                print(f"   [TIP] Intenta cerrar procesos que puedan estar usando estos archivos")
                return False
        except Exception as e:
            print(f"   [ERROR] Error inesperado: {e}")
            return False
    return False

def build_executable():
    """Construye el ejecutable usando PyInstaller"""

    print(f"[BUILD] Construyendo {APP_NAME} v{__version__}")
    print("=" * 60)

    # Limpiar directorios anteriores
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"[CLEAN] Limpiando {dir_name}/")
            if not safe_rmtree(dir_path):
                response = input("\nContinuar de todas formas? (s/n): ").lower()
                if response != 's':
                    print("[CANCEL] Construccion cancelada")
                    return False

    # Determinar punto de entrada
    possible_entries = [
        Path("src/main.py"),
        Path("main.py"),
        Path("src/__main__.py")
    ]

    entry = None
    for entry_path in possible_entries:
        if entry_path.exists():
            entry = entry_path
            break

    if not entry:
        print("[ERROR] No se encontro el archivo de entrada (main.py)")
        return False

    # Nombre del ejecutable
    exe_name = f"ProcesadorFacturas_v{__version__}"

    # Timestamp para directorios únicos (opcional)
    ts = int(time.time())
    work_dir = Path(f"build_{ts}")
    dist_dir = Path("dist")

    # Opciones de PyInstaller
    pyinstaller_args = [
        str(entry),
        "--name", exe_name,
        "--onefile",
        "--windowed",
        "--add-data", "src;src",
        "--hidden-import", "PyQt6",
        "--hidden-import", "openpyxl",
        "--hidden-import", "requests",
        "--hidden-import", "packaging",
        "--collect-all", "PyQt6",
        "--clean",
        "--noconfirm",
        f"--distpath={dist_dir}",
        f"--workpath={work_dir}",
    ]

    print("\n[PYINSTALLER] Ejecutando PyInstaller...")
    print(f"   Nombre: {exe_name}.exe")
    print(f"   Version: {__version__}")
    print(f"   Entry point: {entry}")
    print()

    try:
        PyInstaller.__main__.run(pyinstaller_args)

        exe_path = dist_dir / f"{exe_name}.exe"

        if exe_path.exists():
            print("\n" + "=" * 60)
            print(f"[SUCCESS] Ejecutable creado exitosamente!")
            print(f"[PATH] Ubicacion: {exe_path}")
            print(f"[SIZE] Tamano: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            print("=" * 60)
            return True
        else:
            print(f"\n[ERROR] El ejecutable no se creo en la ubicacion esperada: {exe_path}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error al crear el ejecutable: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
