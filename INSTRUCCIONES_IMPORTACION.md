# Instrucciones para Importar Materiales y Clientes - Lactalis Ventas

## Formato de Archivo para Materiales

Crear un archivo Excel (.xlsx) con los siguientes encabezados en la primera fila:

| CODIGO | DESCRIPCION | SOCIEDAD |
|--------|-------------|----------|
| MAT001 | Leche Entera 1L | 800245795 |
| MAT002 | Yogurt Natural 500ml | 800245795 |
| MAT003 | Queso Mozzarella 250g | 890903711 |

### Descripción de Columnas:
- **CODIGO**: Código único del material (debe coincidir con el código en las facturas XML)
- **DESCRIPCION**: Descripción del material
- **SOCIEDAD**: NIT de la sociedad (vendedor). Ejemplos:
  - `800245795`: Lactalis Colombia S.A.S
  - `890903711`: Procesadora de Leches S.A. - Proleche S.A.

### Notas:
- Los encabezados DEBEN ser exactamente: `CODIGO`, `DESCRIPCION`, `SOCIEDAD`
- Solo se importan materiales nuevos (no duplica materiales existentes)
- La combinación de CODIGO + SOCIEDAD debe ser única

---

## Formato de Archivo para Clientes

Crear un archivo Excel (.xlsx) con los siguientes encabezados en la primera fila:

| Cód.Padre | Nombre Código Padre | NIT |
|-----------|---------------------|-----|
| CLI001 | Supermercado ABC | 900123456 |
| CLI002 | Tienda XYZ | 800987654 |
| CLI003 | Distribuidora 123 | 700456789 |
| CLI004 | Cliente sin NIT | no nit |

### Descripción de Columnas:
- **Cód.Padre**: Código único del cliente
- **Nombre Código Padre**: Nombre del cliente
- **NIT**: Número de identificación tributaria del cliente

### Regla Especial para NIT:
- Si el campo NIT contiene "no nit", "nonit", o "sin nit", el cliente **NO SE REGISTRARÁ**
- Si el campo NIT contiene solo la palabra "nit", se registra pero sin NIT (NULL)
- Cualquier otro valor se registra como NIT válido

### Notas:
- Los encabezados DEBEN ser exactamente: `Cód.Padre`, `Nombre Código Padre`, `NIT`
- Solo se importan clientes nuevos (no duplica clientes existentes)
- El Cód.Padre debe ser único

---

## Cómo Usar

1. **Preparar archivos Excel** con el formato indicado arriba
2. En la aplicación, ir a la pestaña "LACTALIS VENTAS"
3. Click en **"Importar Materiales"** o **"Importar Clientes"**
4. Seleccionar el archivo Excel correspondiente
5. El sistema mostrará:
   - Cantidad de registros nuevos importados
   - Cantidad de registros que ya existían (no duplicados)
   - Cantidad de errores

## Validaciones Durante el Procesamiento

Una vez importados los materiales y clientes, puedes activar las validaciones durante el procesamiento de facturas:

- ☑️ **Validar materiales contra BD**: Solo procesará líneas con materiales que existan en la base de datos
- ☑️ **Validar clientes contra BD**: Solo procesará líneas con clientes que existan en la base de datos

**Nota**: Si las validaciones están desactivadas, se procesarán todas las líneas sin verificar contra la base de datos.

---

## Ubicación de la Base de Datos

- **Windows**: `%APPDATA%\BogotaSAE\database\lactalis_ventas.db`
- **Linux/Mac**: `./database/lactalis_ventas.db`

## Consultas o Problemas

Si tienes problemas con la importación:
1. Verifica que los encabezados sean exactamente como se indican (respeta mayúsculas y acentos)
2. Asegúrate de que el archivo sea .xlsx (Excel)
3. Revisa los logs de la aplicación para más detalles
