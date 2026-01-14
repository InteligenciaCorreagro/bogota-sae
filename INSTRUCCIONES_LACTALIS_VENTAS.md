# 📋 INSTRUCCIONES DE USO - LACTALIS VENTAS

## ⚠️ IMPORTANTE: Orden de Operaciones

Para que las validaciones funcionen correctamente, debes seguir estos pasos EN ORDEN:

---

## 📝 PASO 1: Preparar archivos Excel

### Archivo de Materiales
Crea un archivo Excel con estos encabezados (exactos):
- `CODIGO` - El código del material
- `DESCRIPCION` - Descripción del material
- `SOCIEDAD` - Escribe "Parmalat" o "Proleche" (se convertirá automáticamente al NIT correspondiente)

**Ejemplo:**
```
CODIGO        | DESCRIPCION                    | SOCIEDAD
123456        | Leche entera 1L                | Parmalat
789012        | Yogurt natural 150g            | Proleche
```

**Nota importante sobre SOCIEDAD:**
- Si escribes "Parmalat" o "Lactalis" → se guardará como NIT `800245795` (Lactalis)
- Si escribes "Proleche" o "Procesadora de Leches" → se guardará como NIT `890903711` (Proleche)

---

### Archivo de Clientes
Crea un archivo Excel con estos encabezados (exactos):
- `Cód.Padre` - Código del cliente padre
- `Nombre Código Padre` - Nombre del cliente
- `NIT` - NIT del cliente

**Ejemplo:**
```
Cód.Padre | Nombre Código Padre          | NIT
1001      | Distribuidora XYZ            | 900123456-7
1002      | Supermercados ABC            | 800234567-8
```

**Regla especial:**
- Si el campo NIT contiene "no nit", "sin nit" o "nonit" → el cliente NO se registrará (se omite)

---

## 🗄️ PASO 2: Importar datos a la base de datos

### 2.1. Abrir la aplicación
```bash
python3 app.py
```

### 2.2. Ir al tab "LACTALIS VENTAS"

### 2.3. Importar Materiales
1. Haz clic en el botón **"📦 Importar Materiales"**
2. Selecciona tu archivo Excel de materiales
3. Verás un mensaje indicando cuántos se importaron:
   - ✓ Nuevos: X
   - ⊙ Ya existentes: Y (no se duplican)
   - ✗ Errores: Z

### 2.4. Importar Clientes
1. Haz clic en el botón **"👥 Importar Clientes"**
2. Selecciona tu archivo Excel de clientes
3. Verás un mensaje similar al de materiales

### 2.5. Verificar la importación
Después de importar, verás en la interfaz:
```
Base de datos: /ruta/a/database/lactalis_ventas.db
Materiales: 150 | Clientes: 89
```

Si ves "Materiales: 0" o "Clientes: 0", la importación no funcionó.

---

## 📂 PASO 3: Procesar archivos XML

### 3.1. Activar validaciones (OPCIONAL)
En la sección "Gestión de Base de Datos", activa los checkboxes que necesites:
- ☑ **Validar materiales contra BD** - Solo procesa materiales que existen en la BD
- ☑ **Validar clientes contra BD** - Solo procesa clientes que existen en la BD

⚠️ **MUY IMPORTANTE:**
- Si activas las validaciones pero la BD está vacía, TODAS las líneas serán rechazadas
- Si NO activas las validaciones, se procesarán TODOS los materiales/clientes sin filtrar

### 3.2. Seleccionar carpeta
1. Haz clic en **"📂 SELECCIONAR CARPETA CON ARCHIVOS"**
2. Elige la carpeta que contiene los archivos ZIP y/o XML
3. Confirma el procesamiento

### 3.3. Observar el progreso
Verás mensajes como:
```
[1/1000] Procesando ZIP 1/50: archivo001.zip
[500/1000] Aplicando validaciones a 15000 líneas...
[1000/1000] Escribiendo Excel con 12500 líneas...
```

---

## 🎯 VALIDACIONES QUE SE APLICAN

### Validación de Materiales
Cuando activas "Validar materiales contra BD":

1. El sistema extrae de cada línea del XML:
   - `codigo_subyacente` (código del producto)
   - `nombre_producto` (nombre del producto)

2. Determina la SOCIEDAD según el nombre del producto:
   - Si el nombre contiene "PARMALAT" → Sociedad = `800245795` (Lactalis)
   - Si el nombre contiene "PROLECHE" → Sociedad = `890903711` (Proleche)
   - Si no contiene ninguno → Usa el NIT del vendedor del XML

3. Busca en la BD si existe un material con:
   - `CODIGO` = codigo_subyacente del XML
   - `SOCIEDAD` = la sociedad determinada

4. Si NO existe → **RECHAZA la línea completa** (no se incluye en el Excel final)

### Validación de Clientes
Cuando activas "Validar clientes contra BD":

1. El sistema extrae del XML:
   - `nit_comprador` (NIT del cliente que compró)

2. Busca en la BD si existe un cliente con:
   - `NIT` = nit_comprador del XML

3. Si NO existe → **RECHAZA la línea completa** (no se incluye en el Excel final)

---

## ❓ PREGUNTAS FRECUENTES

### ¿Por qué no está filtrando mis materiales?
**Respuesta:** Probablemente no activaste el checkbox "✓ Validar materiales contra BD" al procesar.

### ¿Por qué todas las líneas fueron rechazadas?
**Respuesta:** La base de datos está vacía. Debes importar materiales y clientes primero.

### ¿Cómo sé si la BD tiene datos?
**Respuesta:** Mira la sección "Gestión de Base de Datos" en la interfaz. Debe decir:
```
Materiales: 150 | Clientes: 89
```
Si dice "0", la BD está vacía.

### ¿Puedo reimportar materiales/clientes?
**Respuesta:** Sí. Los registros existentes no se duplican (se omiten). Solo se agregan los nuevos.

### ¿Qué pasa si no activo ninguna validación?
**Respuesta:** Se procesan TODOS los materiales y clientes del XML sin filtrar. Útil si solo quieres convertir XML a Excel sin validar.

### ¿Dónde está la base de datos?
**Respuesta:** En `bogota-sae/database/lactalis_ventas.db`

---

## 🔍 VERIFICAR BASE DE DATOS (Script de ayuda)

Puedes verificar el contenido de la BD con:

```bash
python3 check_db.py
```

Esto mostrará:
```
📊 REGISTROS EN BASE DE DATOS:
  • Materiales: 150
  • Clientes: 89

✅ Hay 150 materiales en la BD
   Ejemplos:
     - 123456 | Leche entera 1L | 800245795
     - 789012 | Yogurt natural 150g | 890903711
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error: "Base de datos no disponible"
**Solución:** Intenta reiniciar la aplicación. Si persiste, elimina el archivo `database/lactalis_ventas.db` y vuelve a importar.

### Error: "Formato inválido" al importar Excel
**Solución:** Verifica que los encabezados sean EXACTOS:
- Materiales: `CODIGO`, `DESCRIPCION`, `SOCIEDAD`
- Clientes: `Cód.Padre`, `Nombre Código Padre`, `NIT`

### Las validaciones son muy lentas
**Solución:** Esto es normal con volúmenes grandes. La aplicación prioriza estabilidad sobre velocidad. Puede tomar hasta 10 minutos con 20,000+ archivos.

---

## 📊 EJEMPLO COMPLETO DE USO

```bash
# 1. Abrir aplicación
python3 app.py

# 2. En el tab LACTALIS VENTAS:
#    - Clic "Importar Materiales" → seleccionar materiales.xlsx
#    - Clic "Importar Clientes" → seleccionar clientes.xlsx
#    - Verificar que aparezca: "Materiales: X | Clientes: Y"

# 3. Procesar archivos:
#    - ☑ Activar "Validar materiales contra BD"
#    - ☑ Activar "Validar clientes contra BD"
#    - Clic "SELECCIONAR CARPETA CON ARCHIVOS"
#    - Seleccionar carpeta con XMLs
#    - Confirmar y esperar

# 4. Resultado:
#    - Excel generado en: Resultados_LACTALIS_VENTAS_YYYYMMDD_HHMMSS/
#    - Solo contiene líneas que pasaron las validaciones
```

---

**¿Necesitas ayuda?** Revisa los logs de la aplicación para más detalles sobre qué está pasando.
