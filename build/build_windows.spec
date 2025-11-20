# -*- mode: python ; coding: utf-8 -*-
"""
Archivo de configuración de PyInstaller para Windows
Genera un ejecutable standalone de la aplicación

USO:
    pyinstaller build/build_windows.spec

RESULTADO:
    dist/BogotaSAE.exe - Ejecutable único con todas las dependencias
"""

import sys
from pathlib import Path

# Rutas del proyecto
project_root = Path(SPECPATH).parent
src_path = project_root / 'src'

block_cipher = None

# Análisis de archivos y dependencias
a = Analysis(
    [str(project_root / 'app.py')],  # Script principal
    pathex=[str(project_root), str(src_path)],  # Paths de búsqueda
    binaries=[],
    datas=[
        # Incluir plantilla Excel si existe
        (str(project_root / 'Plantilla_REGGIS.xlsx'), '.') if (project_root / 'Plantilla_REGGIS.xlsx').exists() else None,
    ],
    hiddenimports=[
        # Imports que PyInstaller podría no detectar automáticamente
        'openpyxl',
        'openpyxl.cell._writer',
        'openpyxl.styles',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos no necesarios para reducir tamaño
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filtrar None en datas
a.datas = [d for d in a.datas if d is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BogotaSAE',  # Nombre del ejecutable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir con UPX (si está disponible)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No mostrar consola (aplicación GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icono (descomentar y ajustar ruta si tienes un icono)
    # icon=str(project_root / 'build' / 'icon.ico'),
)

# ALTERNATIVA: Generar directorio en lugar de archivo único
# Descomenta el bloque COLLECT y comenta el bloque EXE anterior
# para generar un directorio con el ejecutable y DLLs separadas

# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='BogotaSAE',
# )
