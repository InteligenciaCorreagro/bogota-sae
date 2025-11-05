# Procesador de Facturas Electrónicas - Sistema REGGIS

Sistema unificado para procesar facturas electrónicas XML a formato Excel REGGIS para múltiples clientes.

## Estructura del Proyecto

El proyecto sigue una arquitectura modular separando la **UI** de la **lógica de negocio**:

```
bogota-sae/
├── src/                                    # Código fuente
│   ├── config/                            # Configuraciones
│   │   ├── __init__.py
│   │   ├── constants.py                   # Constantes (NAMESPACES, mapeos)
│   │   └── logging_config.py             # Configuración de logging
│   │
│   ├── ui/                                # Interfaces de usuario (Tkinter)
│   │   ├── __init__.py
│   │   ├── selector_cliente.py           # Ventana de selección de cliente
│   │   └── interfaz_unificada.py         # Interfaz principal de procesamiento
│   │
│   ├── processors/                        # Lógica de procesamiento
│   │   ├── __init__.py
│   │   ├── seaboard_processor.py         # Procesador para SEABOARD
│   │   └── casa_del_agricultor_processor.py  # Procesador para CASA DEL AGRICULTOR
│   │
│   ├── extractors/                        # Extracción de datos
│   │   ├── __init__.py
│   │   └── seaboard_extractor.py         # Extractor de facturas SEABOARD
│   │
│   ├── utils/                             # Utilidades
│   │   ├── __init__.py
│   │   └── sharepoint_detector.py        # Detector de carpetas SharePoint
│   │
│   ├── main.py                            # Punto de entrada de la aplicación
│   └── __init__.py
│
├── run.py                                 # Script de ejecución (recomendado)
├── unified_invoice_processor.py           # Archivo original (obsoleto)
├── .gitignore
└── README.md
```

## Arquitectura

### 1. **Separación de Responsabilidades**

#### **UI (User Interface)**
- `selector_cliente.py`: Interfaz para seleccionar entre SEABOARD y CASA DEL AGRICULTOR
- `interfaz_unificada.py`: Interfaz principal con gestión de archivos y progreso

#### **Procesadores (Business Logic)**
- `seaboard_processor.py`:
  - Procesa archivos XML de SEABOARD
  - Extrae facturas de documentos adjuntos
  - Gestiona conversiones de moneda (USD → COP)
  - Conversiones de unidades (TNE → Kg)

- `casa_del_agricultor_processor.py`:
  - Procesa archivos ZIP con XML
  - Conversiones de unidades (LBR → KG, GRAMOS → KG)
  - Parsing de CDATA en XML

#### **Extractores (Data Extraction)**
- `seaboard_extractor.py`:
  - Extrae datos de facturas XML con namespaces UBL
  - Formatea números al estándar colombiano
  - Calcula totales con IVA

#### **Utilidades (Helpers)**
- `sharepoint_detector.py`: Detecta carpetas sincronizadas de SharePoint/OneDrive
- `constants.py`: Constantes compartidas (NAMESPACES, mapeos de moneda y unidades)
- `logging_config.py`: Configuración centralizada de logging

## Uso

### Ejecutar la aplicación

**Opción 1 (Recomendada)**: Desde la raíz del proyecto:

```bash
python run.py
```

**Opción 2**: Desde el directorio `src`:

```bash
cd src
python main.py
```

**Opción 3**: Como módulo desde la raíz:

```bash
python -m src.main
```

### Flujo de trabajo

1. **Selección de cliente**: Elige entre SEABOARD o CASA DEL AGRICULTOR
2. **Selección de archivos**:
   - SEABOARD: Carpeta con archivos XML (local o SharePoint)
   - CASA DEL AGRICULTOR: Carpeta con archivos ZIP
3. **Procesamiento**: La aplicación extrae y transforma los datos
4. **Resultados**: Archivos Excel en formato REGGIS

## Beneficios de la Nueva Estructura

### ✅ **Mantenibilidad**
- Cada componente tiene una responsabilidad clara
- Fácil localización de bugs y funcionalidades

### ✅ **Escalabilidad**
- Agregar nuevos clientes: crear nuevo procesador en `processors/`
- Agregar nuevos extractores: crear nuevo archivo en `extractors/`

### ✅ **Reutilización**
- Utilidades compartidas en `utils/`
- Constantes centralizadas en `config/`

### ✅ **Testing**
- Cada módulo puede ser testeado independientemente
- Mock de UI para pruebas de lógica de negocio

### ✅ **Colaboración**
- Múltiples desarrolladores pueden trabajar en módulos diferentes
- Reducción de conflictos en control de versiones

## Tecnologías

- **Python 3.x**
- **Tkinter**: Interfaz gráfica
- **openpyxl**: Manipulación de archivos Excel
- **xml.etree.ElementTree**: Parsing de XML
- **zipfile**: Extracción de archivos ZIP

## Clientes Soportados

### 🌐 SEABOARD
- Procesa archivos XML desde SharePoint o carpetas locales
- Soporta conversión de moneda (USD/COP)
- Conversión de toneladas a kilogramos

### 🌾 CASA DEL AGRICULTOR
- Procesa archivos ZIP con XML embebido
- Conversión de libras a kilogramos
- Parsing de unidades en descripción (GRAMOS, GRS)

## Logs

Los logs se generan automáticamente con el formato:
```
procesamiento_facturas_YYYYMMDD_HHMMSS.log
```

## Formato de Salida

Archivos Excel con 24 columnas en formato REGGIS:
- Información de factura
- Datos de producto
- Cantidades y precios
- Información de comprador/vendedor
- Cálculos de IVA
- Totales

## Migración desde el Archivo Original

El archivo `unified_invoice_processor.py` contiene toda la lógica en un solo archivo de 1,100 líneas.
La nueva estructura divide este código en módulos especializados manteniendo toda la funcionalidad.

Para migrar:
1. Usa la nueva estructura en `src/`
2. Mantén el archivo original como backup
3. Una vez verificado, elimina `unified_invoice_processor.py`

## Contribuciones

Al agregar nuevas funcionalidades:
1. Identifica el módulo correcto (UI, processor, extractor, util)
2. Crea nuevos archivos si es necesario
3. Actualiza los imports en `__init__.py`
4. Documenta cambios en este README
