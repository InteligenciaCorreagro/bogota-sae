# Guía de Migración a PyQt6 con Interfaz de Tabs

## 📌 Resumen de Cambios

La aplicación ha sido completamente migrada a una arquitectura moderna con **PyQt6** y una **interfaz basada en tabs**. Esta guía explica los cambios principales y cómo usarlos.

---

## 🎯 Principales Mejoras

### 1. **Nueva Interfaz con Tabs**
- ✅ Todas las funcionalidades en una sola ventana
- ✅ Navegación rápida entre clientes con tabs
- ✅ Interfaz más limpia y moderna
- ✅ Atajos de teclado (Ctrl+1, Ctrl+2, Ctrl+3)

### 2. **Sistema de Auto-Actualización**
- ✅ Verificación automática de actualizaciones al iniciar
- ✅ Descarga e instalación con un click
- ✅ Notificaciones de nuevas versiones

### 3. **Arquitectura Mejorada**
- ✅ Separación clara: UI vs Lógica de Negocio
- ✅ Módulo `core/` para funcionalidades centrales
- ✅ Módulo `ui/tabs/` con tabs independientes
- ✅ Mejor mantenibilidad y escalabilidad

### 4. **Preparado para Distribución**
- ✅ Configuración completa de PyInstaller
- ✅ Scripts de instalador (Inno Setup)
- ✅ Documentación de despliegue

---

## 📁 Comparación de Estructura

### Estructura Anterior

```
bogota-sae/
├── src/
│   ├── ui/
│   │   ├── selector_cliente.py    # Ventana de selección
│   │   └── interfaz_unificada.py  # Ventana de procesamiento
│   ├── processors/
│   ├── extractors/
│   └── main.py
└── run.py
```

### Estructura Nueva ✨

```
bogota-sae/
├── app.py                          # 🆕 Punto de entrada principal
├── src/
│   ├── core/                       # 🆕 Lógica core
│   │   ├── version.py              # Información de versión
│   │   └── updater.py              # Auto-actualización
│   │
│   ├── ui/
│   │   ├── main_window.py          # 🆕 Ventana principal con tabs
│   │   ├── tabs/                   # 🆕 Tabs independientes
│   │   │   ├── tab_seaboard.py
│   │   │   ├── tab_casa_agricultor.py
│   │   │   └── tab_lactalis_compras.py
│   │   │
│   │   ├── selector_cliente.py     # ⚠️ Backup (no usado)
│   │   └── interfaz_unificada.py   # ⚠️ Backup (no usado)
│   │
│   ├── processors/                 # Sin cambios
│   ├── extractors/                 # Sin cambios
│   ├── config/                     # Sin cambios
│   └── utils/                      # Sin cambios
│
├── build/                          # 🆕 Configuración de compilación
│   ├── build_windows.spec
│   ├── build_instructions.md
│   └── installer_script.iss
│
├── README_DEPLOYMENT.md            # 🆕 Guía de despliegue
├── version.json.example            # 🆕 Ejemplo de versión remota
└── MIGRATION_GUIDE.md              # Este archivo
```

---

## 🚀 Cómo Usar la Nueva Aplicación

### Ejecutar en Modo Desarrollo

**Antes:**
```bash
python run.py
# O
cd src && python main.py
```

**Ahora:**
```bash
python app.py
# También funciona:
python run.py
```

### Diferencias en la UI

#### Antes
1. Ventana de selección → Elegir cliente
2. Nueva ventana → Procesamiento
3. Botón "Volver" → Regresar a selector

#### Ahora
1. **Una sola ventana** con tabs
2. Click en tab → Cambiar de cliente
3. Menú de navegación completo
4. Atajos: `Ctrl+1`, `Ctrl+2`, `Ctrl+3`

---

## 🔄 Migración de Código Personalizado

### Si Modificaste la Lógica de Procesamiento

**✅ BUENAS NOTICIAS:** Los procesadores y extractores NO han cambiado.

Los siguientes módulos son **100% compatibles**:
- `src/processors/seaboard_processor.py`
- `src/processors/casa_del_agricultor_processor.py`
- `src/extractors/seaboard_extractor.py`
- `src/config/constants.py`
- `src/utils/sharepoint_detector.py`

### Si Modificaste la Interfaz (UI)

**⚠️ REQUIERE ADAPTACIÓN**

Los archivos de UI han cambiado completamente. Si personalizaste la interfaz:

1. **Ubicar tu código personalizado** en:
   - `src/ui/selector_cliente.py` (antiguo)
   - `src/ui/interfaz_unificada.py` (antiguo)

2. **Migrar a los nuevos tabs:**
   - `src/ui/tabs/tab_seaboard.py`
   - `src/ui/tabs/tab_casa_agricultor.py`
   - `src/ui/tabs/tab_lactalis_compras.py`

3. **Ejemplo de migración:**

   **Antes** (`interfaz_unificada.py`):
   ```python
   def setup_botones_seaboard(self, layout):
       btn = QPushButton("Procesar")
       btn.clicked.connect(self.procesar)
       layout.addWidget(btn)
   ```

   **Ahora** (`tab_seaboard.py`):
   ```python
   def setup_ui(self):
       # ... código de layout ...
       btn = QPushButton("Procesar")
       btn.clicked.connect(self.procesar_carpeta_xml)
       # ... resto del código ...
   ```

---

## 🆕 Nuevas Funcionalidades

### 1. Sistema de Auto-Actualización

```python
from core.updater import Updater

# En tu código
updater = Updater(parent_widget)
updater.check_for_updates()
```

### 2. Información de Versión

```python
from core.version import __version__, get_version_string

print(get_version_string())  # "Procesador de Facturas v2.0.0"
```

### 3. Menú de Aplicación

Accesible desde la barra de menú:
- **Archivo** → Salir
- **Herramientas** → Buscar Actualizaciones, Logs
- **Vista** → Cambiar entre tabs
- **Ayuda** → Acerca de, Documentación

---

## 📝 Tareas Post-Migración

### Para Desarrolladores

- [ ] Probar todas las funcionalidades en modo desarrollo
- [ ] Verificar que procesadores funcionan correctamente
- [ ] Personalizar tab de Lactalis si es necesario
- [ ] Configurar URL de auto-actualización en `core/version.py`

### Para Distribución

- [ ] Compilar ejecutable: `pyinstaller build/build_windows.spec`
- [ ] Probar ejecutable en máquina limpia
- [ ] Crear instalador con Inno Setup
- [ ] Configurar GitHub Releases
- [ ] Publicar `version.json` en servidor/GitHub

---

## 🔧 Personalización del Tab Lactalis Compras

El tab **Lactalis Compras** está implementado como **plantilla** lista para personalizar:

### Características Actuales
- ✅ Interfaz completa con campos configurables
- ✅ Procesamiento en segundo plano
- ✅ Usa procesador de SEABOARD como base temporal
- ⚠️ Requiere procesador específico para Lactalis

### Personalizar para Lactalis

1. **Crear procesador específico:**

   ```python
   # src/processors/lactalis_processor.py
   class ProcesadorLactalis:
       def __init__(self, carpeta_xml, plantilla_excel):
           # ... lógica específica de Lactalis ...

       def procesar(self):
           # ... implementación ...
           pass
   ```

2. **Actualizar el tab:**

   ```python
   # src/ui/tabs/tab_lactalis_compras.py
   from processors.lactalis_processor import ProcesadorLactalis

   # Línea ~223: Cambiar
   procesador = ProcesadorSeaboard(...)  # Temporal
   # Por:
   procesador = ProcesadorLactalis(...)  # Específico
   ```

3. **Agregar validaciones específicas** según necesidades de Lactalis

---

## ❓ FAQ - Preguntas Frecuentes

### ¿Los archivos antiguos siguen funcionando?

**Sí**, puedes seguir usando:
```bash
python run.py    # Funciona con nueva estructura
cd src && python main.py  # También funciona
```

### ¿Debo eliminar `selector_cliente.py` e `interfaz_unificada.py`?

**No inmediatamente**. Están en el proyecto como backup. Una vez verificado que todo funciona, puedes eliminarlos.

### ¿Cómo actualizo la versión de la app?

1. Editar `src/core/version.py`:
   ```python
   __version__ = "2.1.0"
   ```

2. Compilar nuevo ejecutable
3. Actualizar `version.json` en servidor

### ¿Cómo agrego un nuevo cliente/tab?

1. **Crear archivo del tab:**
   ```python
   # src/ui/tabs/tab_nuevo_cliente.py
   class TabNuevoCliente(QWidget):
       def __init__(self):
           super().__init__()
           self.setup_ui()

       def setup_ui(self):
           # ... interfaz ...
   ```

2. **Registrar en `__init__.py`:**
   ```python
   # src/ui/tabs/__init__.py
   from .tab_nuevo_cliente import TabNuevoCliente
   ```

3. **Agregar a MainWindow:**
   ```python
   # src/ui/main_window.py
   self.tab_nuevo = TabNuevoCliente()
   self.tab_widget.addTab(self.tab_nuevo, "🆕 NUEVO CLIENTE")
   ```

---

## 📞 Soporte

Si tienes problemas con la migración:

1. Revisar logs en el directorio actual (`.log`)
2. Consultar `README_DEPLOYMENT.md` para más detalles
3. Crear issue en GitHub: https://github.com/InteligenciaCorreagro/bogota-sae/issues

---

## ✅ Checklist de Verificación

- [ ] La aplicación inicia correctamente con `python app.py`
- [ ] Los 3 tabs son visibles (SEABOARD, CASA, LACTALIS)
- [ ] El procesamiento de SEABOARD funciona
- [ ] El procesamiento de CASA DEL AGRICULTOR funciona
- [ ] El menú de navegación es accesible
- [ ] Los atajos de teclado funcionan (Ctrl+1, Ctrl+2, Ctrl+3)
- [ ] El sistema de auto-actualización está configurado
- [ ] El ejecutable se compila sin errores
- [ ] El ejecutable funciona en otra máquina Windows

---

## 🎉 Conclusión

La migración a PyQt6 con interfaz de tabs proporciona:
- ✨ Mejor experiencia de usuario
- 🚀 Más fácil mantenimiento
- 📦 Listo para distribución profesional
- 🔄 Auto-actualización integrada

¡Disfruta de la nueva versión!
