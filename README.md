# Sistema SAE - Procesador de Facturas Electrónicas

Sistema profesional para el procesamiento de facturas electrónicas XML a formato Excel REGGIS.

## 🚀 Características

- **Interfaz Profesional PyQt6**: Diseño moderno y empresarial
- **Actualización Automática**: El sistema se actualiza automáticamente desde GitHub
- **Multi-Cliente**: Soporte para múltiples clientes:
  - 🌐 **SEABOARD**: Procesamiento desde SharePoint/Local
  - 🌾 **CASA DEL AGRICULTOR**: Procesamiento desde archivos ZIP
  - 🥛 **LACTALIS**: Módulo en desarrollo

## 📋 Requisitos

- Python 3.8 o superior
- Conexión a Internet (para actualizaciones automáticas)

## 🔧 Instalación

### Windows

1. **Instalar Dependencias**:
   - Haga doble clic en `INSTALAR.bat`
   - Espere a que se instalen todas las dependencias

2. **Iniciar el Sistema**:
   - Haga doble clic en `INICIAR.bat`

### Linux/Mac

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar sistema
python sae_pyqt6.py
```

## 📖 Uso

### 1. Selección de Cliente

Al iniciar, seleccione el cliente que desea procesar:

- **SEABOARD**: Para facturas desde SharePoint o carpetas locales
- **CASA DEL AGRICULTOR**: Para facturas en archivos ZIP
- **LACTALIS**: Módulo en configuración (contacte al administrador)

### 2. SEABOARD

**Opciones:**
- **SharePoint Sincronizado**: El sistema detecta automáticamente carpetas de SharePoint
- **Carpeta Local**: Seleccione manualmente una carpeta con archivos XML

**Proceso:**
1. Seleccione la opción deseada
2. Elija la carpeta con los archivos XML
3. Confirme el procesamiento
4. Los resultados se guardan en `Resultados_SEABOARD/`

### 3. Casa del Agricultor

**Proceso:**
1. Seleccione la carpeta con archivos ZIP
2. Confirme el procesamiento
3. Los resultados se guardan en `Resultados_CASA_DEL_AGRICULTOR/`

**Conversiones automáticas:**
- Libras (LBR) → Kilogramos (KG)
- Gramos → Kilogramos
- Unidades estándar UBL → Formato REGGIS

### 4. Lactalis

Este módulo está en desarrollo. Para configurarlo:

1. Contacte al administrador del sistema
2. Proporcione:
   - Formato de archivos de entrada
   - Estructura de datos esperada
   - Reglas de conversión específicas
   - Formato de salida deseado

## 🔄 Actualización Automática

El sistema verifica automáticamente actualizaciones al iniciar:

1. Si hay una actualización disponible, aparecerá un diálogo
2. Puede elegir actualizar ahora o más tarde
3. Si actualiza, la aplicación se reiniciará automáticamente

**Actualización Manual:**

```bash
python auto_updater.py
```

## 📁 Estructura de Archivos

```
bogota-sae/
├── sae_pyqt6.py              # Aplicación principal con PyQt6
├── unified_invoice_processor.py  # Versión anterior (tkinter)
├── auto_updater.py           # Sistema de actualización
├── requirements.txt          # Dependencias
├── version.json              # Información de versión
├── INSTALAR.bat              # Instalador Windows
├── INICIAR.bat               # Iniciador Windows
├── README.md                 # Este archivo
├── Plantilla_REGGIS.xlsx     # Plantilla Excel (se crea automáticamente)
├── Resultados_SEABOARD/      # Resultados de SEABOARD
└── Resultados_CASA_DEL_AGRICULTOR/  # Resultados Casa del Agricultor
```

## 🐛 Solución de Problemas

### Error al instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Error "PyQt6 no encontrado"

```bash
pip install PyQt6==6.6.1
```

### El sistema no detecta SharePoint

- Verifique que OneDrive/SharePoint esté sincronizado
- Use la opción "Carpeta Local" como alternativa

### Error de actualización

- Verifique su conexión a Internet
- Intente actualizar manualmente: `python auto_updater.py`

## 📝 Formato de Salida

El sistema genera archivos Excel con el formato REGGIS estándar:

| Columna | Descripción |
|---------|-------------|
| N° Factura | Número de factura |
| Nombre Producto | Nombre del producto |
| Codigo Subyacente | Código del producto |
| Unidad Medida | Kg, Un, Lt |
| Cantidad | Cantidad (5 decimales) |
| Precio Unitario | Precio (5 decimales) |
| ... | 24 columnas en total |

## 🔐 Seguridad

- El sistema solo lee archivos XML/ZIP
- No modifica archivos originales
- Crea copias de seguridad automáticas al actualizar
- Logs de procesamiento para auditoría

## 📞 Soporte

Para soporte técnico o configuración de nuevos clientes:

- Revise los logs en la carpeta principal
- Contacte al administrador del sistema
- GitHub: https://github.com/InteligenciaCorreagro/bogota-sae

## 📜 Historial de Versiones

### Versión 2.0.0 (2025-11-04)
- ✨ Nueva interfaz PyQt6 profesional
- 🔄 Sistema de actualización automática
- 🥛 Agregado módulo Lactalis (en desarrollo)
- 🎨 Diseño empresarial mejorado
- 📱 Mejor experiencia de usuario

### Versión 1.0.0
- Versión inicial con tkinter
- Soporte SEABOARD y Casa del Agricultor

## 📄 Licencia

Sistema desarrollado por REGGIS para InteligenciaCorreagro.

---

**¡Gracias por usar el Sistema SAE!** 🚀
