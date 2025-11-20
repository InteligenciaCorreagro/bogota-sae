# Guía de Despliegue y Distribución

Esta guía explica cómo ejecutar, compilar y distribuir la aplicación Procesador de Facturas Electrónicas REGGIS.

## 📋 Tabla de Contenidos

1. [Ejecución en Modo Desarrollo](#ejecución-en-modo-desarrollo)
2. [Compilación a Ejecutable Windows](#compilación-a-ejecutable-windows)
3. [Sistema de Auto-Actualización](#sistema-de-auto-actualización)
4. [Distribución y Publicación](#distribución-y-publicación)
5. [Solución de Problemas](#solución-de-problemas)

---

## 🚀 Ejecución en Modo Desarrollo

### Requisitos

- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)

### Instalación de Dependencias

```bash
# Desde el directorio raíz del proyecto
pip install -r requirements.txt
```

### Ejecutar la Aplicación

**Opción 1 (Recomendada):** Usar el punto de entrada principal

```bash
python app.py
```

**Opción 2:** Usar el script run.py (compatible con versión anterior)

```bash
python run.py
```

**Opción 3:** Ejecutar como módulo

```bash
python -m src.main
```

### Estructura de la Nueva Aplicación

```
bogota-sae/
├── app.py                          # 🆕 Punto de entrada principal
├── src/
│   ├── main.py                     # Punto de entrada alternativo
│   ├── core/                       # 🆕 Lógica de negocio core
│   │   ├── version.py              # Información de versión
│   │   └── updater.py              # Sistema de auto-actualización
│   │
│   ├── ui/                         # Interfaces de usuario
│   │   ├── main_window.py          # 🆕 Ventana principal con tabs
│   │   └── tabs/                   # 🆕 Tabs individuales
│   │       ├── tab_seaboard.py
│   │       ├── tab_casa_agricultor.py
│   │       └── tab_lactalis_compras.py
│   │
│   ├── processors/                 # Procesadores de datos
│   ├── extractors/                 # Extractores de XML
│   ├── config/                     # Configuraciones
│   └── utils/                      # Utilidades
│
├── build/                          # 🆕 Configuración de compilación
│   ├── build_windows.spec          # Configuración PyInstaller
│   └── build_instructions.md       # Instrucciones detalladas
│
└── requirements.txt
```

---

## 📦 Compilación a Ejecutable Windows

### Requisitos Adicionales

```bash
pip install pyinstaller
```

### Compilar con PyInstaller

**Método 1 (Recomendado):** Usar archivo .spec

```bash
# Desde el directorio raíz
pyinstaller build/build_windows.spec
```

**Método 2:** Comando directo

```bash
pyinstaller --name BogotaSAE ^
            --onefile ^
            --windowed ^
            --hidden-import openpyxl ^
            --hidden-import PyQt6.QtCore ^
            --hidden-import PyQt6.QtWidgets ^
            --hidden-import PyQt6.QtGui ^
            app.py
```

### Resultado de la Compilación

El ejecutable se generará en:

```
dist/
└── BogotaSAE.exe          # Ejecutable standalone (~80-120 MB)
```

### Opciones de Compilación

| Opción | Descripción | Ventajas | Desventajas |
|--------|-------------|----------|-------------|
| `--onefile` | Un solo archivo .exe | Fácil distribución | Arranque más lento |
| `--onedir` | Directorio con .exe y DLLs | Arranque rápido | Múltiples archivos |
| `--windowed` | Sin consola | Aplicación limpia | No muestra errores en consola |
| `--console` | Con consola | Debug más fácil | Ventana extra visible |

### Optimización del Tamaño

El archivo .spec ya está optimizado para excluir módulos innecesarios:
- ❌ tkinter
- ❌ matplotlib
- ❌ numpy
- ❌ pandas
- ❌ scipy

**Tamaño esperado:** 80-120 MB (normal para aplicaciones PyQt6)

---

## 🔄 Sistema de Auto-Actualización

### Configuración

La aplicación incluye un sistema de auto-actualización integrado que verifica nuevas versiones al iniciar.

### Archivo de Versión Remota (version.json)

Crea un archivo `version.json` en tu repositorio o servidor:

```json
{
    "version": "2.1.0",
    "build_date": "2025-12-01",
    "release_notes": "
        • Nueva funcionalidad de exportación masiva<br>
        • Mejoras de rendimiento en procesamiento XML<br>
        • Corrección de errores en módulo Lactalis
    ",
    "download_url": "https://github.com/usuario/bogota-sae/releases/download/v2.1.0/BogotaSAE_v2.1.0_Setup.exe",
    "min_version_required": "2.0.0",
    "critical_update": false
}
```

### Configurar URL de Actualización

Edita `src/core/version.py`:

```python
VERSION_INFO = {
    # ...
    'update_check_url': 'https://tu-dominio.com/path/version.json',
    'download_url_base': 'https://github.com/usuario/repo/releases/download',
    # ...
}
```

### Flujo de Actualización

1. **Al iniciar:** La app verifica actualizaciones automáticamente (silencioso si está actualizada)
2. **Manualmente:** Usuario puede ir a `Herramientas → Buscar Actualizaciones`
3. **Nueva versión disponible:**
   - Muestra diálogo con notas de versión
   - Usuario acepta descargar
   - Descarga en segundo plano con barra de progreso
   - Ejecuta instalador automáticamente
   - Cierra aplicación para completar actualización

### Publicar Nueva Versión

1. **Actualizar versión en código:**

   ```python
   # src/core/version.py
   __version__ = "2.1.0"
   ```

2. **Compilar ejecutable:**

   ```bash
   pyinstaller build/build_windows.spec
   ```

3. **Crear instalador** (opcional, ver sección siguiente)

4. **Subir a GitHub Releases:**

   ```bash
   # Crear tag
   git tag v2.1.0
   git push origin v2.1.0

   # Crear release en GitHub
   # Subir BogotaSAE.exe o instalador
   ```

5. **Actualizar version.json:**

   ```json
   {
       "version": "2.1.0",
       "download_url": "https://github.com/usuario/repo/releases/download/v2.1.0/BogotaSAE_v2.1.0.exe",
       ...
   }
   ```

---

## 📤 Distribución y Publicación

### Opción 1: Distribución Simple (Solo .exe)

**Ventajas:**
- Rápido y simple
- Un solo archivo para distribuir

**Pasos:**
1. Compilar con PyInstaller
2. Subir `dist/BogotaSAE.exe` a GitHub Releases
3. Usuarios descargan y ejecutan directamente

### Opción 2: Instalador con Inno Setup (Recomendado)

**Ventajas:**
- Instalación profesional
- Acceso directo en menú inicio
- Desinstalador automático
- Asociación de archivos (opcional)

**Pasos:**

1. **Descargar Inno Setup:** https://jrsoftware.org/isinfo.php

2. **Crear script de instalación** (`build/installer_script.iss`):

```iss
[Setup]
AppName=Procesador de Facturas REGGIS
AppVersion=2.0.0
DefaultDirName={autopf}\BogotaSAE
DefaultGroupName=Procesador de Facturas
OutputDir=installer_output
OutputBaseFilename=BogotaSAE_v2.0.0_Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\BogotaSAE.exe"; DestDir: "{app}"
Source: "Plantilla_REGGIS.xlsx"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Procesador de Facturas"; Filename: "{app}\BogotaSAE.exe"
Name: "{autodesktop}\Procesador de Facturas"; Filename: "{app}\BogotaSAE.exe"

[Run]
Filename: "{app}\BogotaSAE.exe"; Description: "Ejecutar aplicación"; Flags: postinstall nowait skipifsilent
```

3. **Compilar instalador:**
   - Abrir Inno Setup Compiler
   - Cargar `installer_script.iss`
   - Compilar

4. **Resultado:** `installer_output/BogotaSAE_v2.0.0_Setup.exe`

### Opción 3: Portable (Sin instalación)

**Ventajas:**
- No requiere instalación
- Ejecutar desde USB

**Pasos:**
1. Compilar con PyInstaller en modo `--onedir`
2. Comprimir carpeta `dist/BogotaSAE/` a ZIP
3. Distribuir archivo ZIP

---

## 🔧 Solución de Problemas

### Error: "No module named 'PyQt6'"

```bash
pip install PyQt6
```

### Error: "No module named 'openpyxl'"

```bash
pip install openpyxl
```

### El ejecutable no inicia

1. **Ejecutar desde CMD para ver errores:**

   ```bash
   cd dist
   BogotaSAE.exe
   ```

2. **Compilar con modo debug:**

   ```bash
   pyinstaller --debug all build/build_windows.spec
   ```

3. **Verificar que todas las dependencias estén incluidas**

### Errores de rutas relativas

Si la aplicación busca archivos en rutas incorrectas:

```python
# Usar Path relativo al ejecutable
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Ejecutable de PyInstaller
    base_path = Path(sys._MEIPASS)
else:
    # Modo desarrollo
    base_path = Path(__file__).parent

plantilla = base_path / "Plantilla_REGGIS.xlsx"
```

### Ejecutable muy grande (>150 MB)

**Es normal** para aplicaciones PyQt6. PyQt6 incluye muchas bibliotecas Qt.

**Reducir tamaño:**
- Usar `--onedir` en lugar de `--onefile`
- Excluir módulos no usados (ya configurado)
- Comprimir con UPX (ya configurado)

### Windows SmartScreen bloquea el ejecutable

**Soluciones:**

1. **Firma de código** (requiere certificado):
   ```bash
   signtool sign /f certificado.pfx /p password BogotaSAE.exe
   ```

2. **Distribuir con instalador firmado**

3. **Instrucciones para usuarios:**
   - Click derecho → Propiedades
   - Marcar "Desbloquear"
   - Aceptar

---

## 📝 Checklist de Release

- [ ] Actualizar versión en `src/core/version.py`
- [ ] Actualizar `README.md` con nuevas funcionalidades
- [ ] Probar aplicación en modo desarrollo
- [ ] Compilar ejecutable con PyInstaller
- [ ] Probar ejecutable en máquina limpia
- [ ] Crear instalador (si aplica)
- [ ] Crear tag de git: `git tag v2.x.x`
- [ ] Crear GitHub Release
- [ ] Subir ejecutable/instalador a Release
- [ ] Actualizar `version.json` con nueva versión
- [ ] Verificar que auto-actualización funcione
- [ ] Notificar a usuarios

---

## 🔗 Referencias

- **PyInstaller:** https://pyinstaller.org/
- **PyQt6:** https://www.riverbankcomputing.com/software/pyqt/
- **Inno Setup:** https://jrsoftware.org/isinfo.php
- **GitHub Releases:** https://docs.github.com/en/repositories/releasing-projects-on-github

---

## 💡 Consejos Adicionales

### Versionado Semántico

Usa **Semantic Versioning** (X.Y.Z):
- **X (Major):** Cambios incompatibles
- **Y (Minor):** Nueva funcionalidad compatible
- **Z (Patch):** Correcciones de bugs

### Mantener Changelog

Documenta cambios en cada versión para los usuarios.

### Testing Antes de Release

- Probar en máquina sin Python instalado
- Probar procesamiento con datos reales
- Verificar auto-actualización
- Probar instalador/desinstalador

---

## 📧 Soporte

Para problemas o sugerencias, crear un issue en GitHub o contactar al equipo de desarrollo.
