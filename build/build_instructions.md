# Instrucciones de Compilación - PyInstaller

## Requisitos Previos

1. **Python 3.8 o superior** instalado
2. **PyInstaller** instalado:
   ```bash
   pip install pyinstaller
   ```

3. **Todas las dependencias** del proyecto instaladas:
   ```bash
   pip install -r requirements.txt
   ```

## Generar Ejecutable para Windows

### Opción 1: Usando archivo .spec (Recomendado)

```bash
# Desde el directorio raíz del proyecto
pyinstaller build/build_windows.spec
```

### Opción 2: Comando directo

```bash
pyinstaller --name BogotaSAE ^
            --onefile ^
            --windowed ^
            --add-data "Plantilla_REGGIS.xlsx;." ^
            --hidden-import openpyxl ^
            --hidden-import PyQt6.QtCore ^
            --hidden-import PyQt6.QtWidgets ^
            --hidden-import PyQt6.QtGui ^
            app.py
```

**Nota para Linux/Mac:** Reemplazar `;` por `:` en `--add-data`

## Opciones de Compilación

### Ejecutable único (onefile)
- **Ventaja:** Un solo archivo .exe, fácil de distribuir
- **Desventaja:** Arranque más lento (extrae archivos en temporal)
- Usar en archivo .spec: `EXE(..., onefile=True, ...)`

### Directorio con ejecutable (onedir)
- **Ventaja:** Arranque más rápido
- **Desventaja:** Múltiples archivos para distribuir
- Descomentar bloque `COLLECT` en archivo .spec

## Ubicación de Archivos Generados

```
dist/
├── BogotaSAE.exe          # Ejecutable (modo onefile)
└── BogotaSAE/             # Directorio (modo onedir)
    ├── BogotaSAE.exe
    ├── _internal/         # DLLs y dependencias
    └── ...
```

## Reducir Tamaño del Ejecutable

1. **Excluir módulos no usados** (ya configurado en .spec):
   - tkinter, matplotlib, numpy, etc.

2. **Usar UPX para comprimir** (si está instalado):
   ```bash
   # Instalar UPX
   # Windows: descargar de https://upx.github.io/
   # Linux: sudo apt install upx-ucl
   ```

3. **Usar modo onedir** en lugar de onefile

## Solución de Problemas Comunes

### Error: "No module named 'PyQt6'"
```bash
pip install PyQt6
```

### Error: "No module named 'openpyxl'"
```bash
pip install openpyxl
```

### El ejecutable es muy grande (>100 MB)
- Normal para aplicaciones PyQt6
- PyQt6 incluye muchas bibliotecas Qt
- Usar modo onedir puede ayudar

### Error al iniciar el ejecutable
1. Ejecutar desde CMD para ver errores:
   ```bash
   BogotaSAE.exe
   ```

2. Verificar logs en directorio temporal

3. Generar con `--debug all` para más información:
   ```bash
   pyinstaller --debug all build/build_windows.spec
   ```

## Crear Instalador (Opcional)

### Usando Inno Setup (Windows)

1. Descargar Inno Setup: https://jrsoftware.org/isinfo.php
2. Crear script .iss (ver ejemplo en `build/installer_script.iss`)
3. Compilar con Inno Setup Compiler

### Usando NSIS (Windows)

1. Descargar NSIS: https://nsis.sourceforge.io/
2. Crear script .nsi
3. Compilar con makensis

## Firmar el Ejecutable (Opcional)

Para evitar advertencias de Windows SmartScreen:

```bash
# Requiere certificado de firma de código
signtool sign /f certificado.pfx /p password /t http://timestamp.digicert.com BogotaSAE.exe
```

## Distribución

1. **Ejecutable simple:**
   - Subir `dist/BogotaSAE.exe` a GitHub Releases

2. **Con instalador:**
   - Crear instalador con Inno Setup/NSIS
   - Subir instalador a GitHub Releases

3. **Actualizar version.json:**
   ```json
   {
       "version": "2.0.0",
       "download_url": "https://github.com/usuario/repo/releases/download/v2.0.0/BogotaSAE_v2.0.0_Setup.exe",
       "release_notes": "..."
   }
   ```

## Referencias

- PyInstaller Docs: https://pyinstaller.org/
- PyQt6 Docs: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Inno Setup: https://jrsoftware.org/isinfo.php
