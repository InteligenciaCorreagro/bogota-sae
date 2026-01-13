# 🔍 Guía de Debugging para Crash

El programa ahora tiene **protección completa contra crashes** y **logging detallado** para identificar problemas.

## 📋 Pasos para Identificar el Problema

### PASO 1: Prueba Simple de Base de Datos

Ejecuta este script para verificar que todo funcione sin la UI:

```bash
cd /home/user/bogota-sae
python3 test_db_simple.py
```

**Este script prueba:**
- ✅ Que `openpyxl` se pueda importar
- ✅ Que `sqlite3` se pueda importar
- ✅ Que `LactalisDatabase` se pueda crear
- ✅ Que la base de datos funcione correctamente
- ✅ Que `ExcelImporter` esté disponible

**Si hay error aquí**, verás exactamente en qué paso falla con el stack trace completo.

---

### PASO 2: Lanzar Aplicación con Debugging

Ejecuta este script para lanzar la aplicación con logging máximo:

```bash
cd /home/user/bogota-sae
python3 debug_app.py
```

**Este script:**
- 📝 Guarda TODOS los logs en `debug_app.log`
- 📺 Muestra logs en pantalla en tiempo real
- 🔍 Captura el error exacto si hay crash
- 🎯 Identifica en qué línea de código falla

**Si crashea**, revisa el archivo `debug_app.log`:
```bash
cat debug_app.log
```

---

## 🛡️ Protecciones Implementadas

El programa ahora tiene protección contra:

1. **Error al inicializar base de datos**
   - Si falla, muestra: "Base de datos: No disponible (error de inicialización)"
   - La aplicación continúa funcionando sin validaciones
   - Los logs muestran el error exacto

2. **Error al importar materiales/clientes**
   - Verifica que BD esté disponible antes de importar
   - Muestra mensaje claro si BD no disponible
   - Logging de cada paso de importación

3. **Error al validar archivos**
   - Manejo de excepciones en cada método
   - Mensajes descriptivos de errores
   - Logging detallado de problemas

---

## 📊 Interpretando los Logs

### Logs Normales (Todo OK):

```
INFO - Creando directorio de base de datos: ./database
INFO - Ruta de base de datos: ./database/lactalis_ventas.db
INFO - Conectado a base de datos: ./database/lactalis_ventas.db
INFO - Tablas creadas/verificadas exitosamente
INFO - Base de datos inicializada correctamente
```

### Logs de Error (Hay Problema):

```
ERROR - Error en __init__ de LactalisDatabase: [mensaje de error]
ERROR - Stack trace completo:
Traceback (most recent call last):
  ...
```

---

## 🔧 Soluciones Comunes

### Error: "No module named 'openpyxl'"
```bash
pip3 install openpyxl
```

### Error: "Permission denied" al crear carpeta
```bash
# Usar carpeta local en lugar de APPDATA
# Editar src/database/lactalis_database.py línea 40:
base_dir = Path.cwd() / 'database'
```

### Error: "Database is locked"
```bash
# Cerrar otras instancias de la aplicación
# O eliminar el archivo de BD:
rm database/lactalis_ventas.db
```

---

## 📞 Información para Soporte

Si sigues teniendo problemas, proporciona:

1. **Salida completa de test_db_simple.py**
2. **Contenido completo de debug_app.log**
3. **Sistema operativo**: `uname -a` (Linux) o `ver` (Windows)
4. **Versión de Python**: `python3 --version`
5. **Librerías instaladas**: `pip3 list`

---

## ✅ Verificación Final

**Para confirmar que todo funciona:**

1. ✅ `test_db_simple.py` debe mostrar: "✅ TODAS LAS PRUEBAS PASARON"
2. ✅ `debug_app.py` debe abrir la aplicación sin errores
3. ✅ En la app, debe mostrar: "Base de datos: [ruta]" con contadores de materiales/clientes

Si alguno de estos falla, revisa los logs detallados que proporcionan.
