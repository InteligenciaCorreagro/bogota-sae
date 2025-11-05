# Guía de Deployment y Actualización

Esta guía explica cómo generar ejecutables y publicar actualizaciones que se instalarán automáticamente en las máquinas de los usuarios.

## 📦 Sistema de Auto-Actualización

La aplicación incluye un sistema de actualización automática que:
- ✅ Verifica actualizaciones al iniciar
- ✅ Descarga e instala automáticamente
- ✅ Reinicia la aplicación con la nueva versión
- ✅ No requiere intervención técnica del usuario

## 🔄 Proceso de Actualización para Usuarios Finales

1. **El usuario abre la aplicación**
2. **La aplicación verifica automáticamente** si hay una nueva versión en GitHub
3. **Si hay actualización disponible**, muestra un diálogo:
   - Versión actual vs. nueva versión
   - Notas de la versión
   - Botones: "Actualizar Ahora" o "Más Tarde"
4. **Si el usuario acepta**:
   - Descarga la actualización con barra de progreso
   - Instala automáticamente
   - Reinicia la aplicación
5. **Todo el proceso es transparente** y sin errores

## 🚀 Publicar una Nueva Versión (Para Desarrolladores)

### Paso 1: Actualizar la Versión

Edita el archivo `src/config/version.py`:

```python
__version__ = "1.0.1"  # Incrementa la versión
```

### Paso 2: Commit y Push

```bash
git add .
git commit -m "Release: v1.0.1 - Descripción de cambios"
git push origin main
```

### Paso 3: Crear y Publicar el Tag

```bash
# Crear tag con la nueva versión
git tag -a v1.0.1 -m "Release v1.0.1"

# Push del tag a GitHub
git push origin v1.0.1
```

### Paso 4: GitHub Actions Automático

Una vez que pusheas el tag:

1. **GitHub Actions se activa automáticamente**
2. **Compila la aplicación** en Windows
3. **Crea el ejecutable** con PyInstaller
4. **Publica un Release** en GitHub con:
   - El ejecutable (.exe)
   - Notas de la versión
   - Assets descargables

### Paso 5: Usuarios Reciben la Actualización

- **Próxima vez que abran la app**: verán el diálogo de actualización
- **Proceso automático**: descargan e instalan sin intervención
- **Sin errores**: todo está automatizado

## 🛠️ Generar Ejecutable Manualmente (Opcional)

Si necesitas generar el ejecutable localmente:

### En Windows:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Generar ejecutable
python build_exe.py
```

El ejecutable estará en: `dist/ProcesadorFacturas_vX.X.X.exe`

## 📋 Versionado Semántico

Usamos versionado semántico (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR** (1.x.x): Cambios incompatibles con versiones anteriores
- **MINOR** (x.1.x): Nuevas funcionalidades compatibles
- **PATCH** (x.x.1): Correcciones de bugs

### Ejemplos:

- `v1.0.0` → Primera versión estable
- `v1.1.0` → Agregado soporte para nuevo cliente
- `v1.1.1` → Corregido bug en procesamiento
- `v2.0.0` → Cambio mayor en arquitectura

## 🔧 Configuración del Auto-Updater

En `src/config/version.py`:

```python
# Habilitar/deshabilitar auto-actualización
AUTO_UPDATE_ENABLED = True

# Verificar al inicio
CHECK_UPDATE_ON_STARTUP = True

# Intervalo de verificación (horas)
UPDATE_CHECK_INTERVAL_HOURS = 24
```

## 🔍 Verificación Manual de Actualizaciones

Los usuarios también pueden verificar manualmente desde el menú (si se implementa).

## 📊 Monitoreo de Actualizaciones

### Ver quién descargó la actualización:

1. Ve a GitHub → Releases
2. Click en la versión específica
3. Ve las **estadísticas de descarga** de cada asset

### Logs de actualización:

Los logs de actualización se guardan en:
```
procesamiento_facturas_YYYYMMDD_HHMMSS.log
```

## ⚠️ Troubleshooting

### Si la actualización falla:

1. **Error de red**: Verificar conexión a internet
2. **Error de permisos**: Ejecutar como administrador
3. **Antivirus bloqueando**: Agregar excepción

### Actualización manual (plan B):

1. Ir a: https://github.com/InteligenciaCorreagro/bogota-sae/releases
2. Descargar el último `ProcesadorFacturas.exe`
3. Reemplazar el ejecutable antiguo

## 🎯 Resumen del Flujo

```
Desarrollador                GitHub                  Usuario
    |                          |                        |
    | 1. Incrementa versión    |                        |
    | 2. git tag v1.0.1        |                        |
    | 3. git push --tags   --> |                        |
    |                          | 4. GitHub Actions      |
    |                          | 5. Build .exe          |
    |                          | 6. Create Release  --> |
    |                          |                        | 7. Abre la app
    |                          |                        | 8. Ve diálogo
    |                          | <-- 9. Descarga .exe   |
    |                          |                        | 10. Instala
    |                          |                        | 11. Reinicia
    |                          |                        | ✅ Actualizado!
```

## 📝 Checklist para Nueva Release

- [ ] Actualizar versión en `src/config/version.py`
- [ ] Probar la aplicación localmente
- [ ] Commit con mensaje descriptivo
- [ ] Push a main
- [ ] Crear y push tag `vX.X.X`
- [ ] Verificar que GitHub Actions se ejecute correctamente
- [ ] Verificar que el Release se publique
- [ ] Probar descarga del ejecutable
- [ ] Confirmar que los usuarios reciben la notificación

## 🔐 Seguridad

- Las actualizaciones se descargan **solo desde GitHub Releases oficial**
- Se verifica la **integridad** del archivo descargado
- El proceso requiere **confirmación del usuario**
- Los archivos antiguos se **respaldan** antes de reemplazar

## 🆘 Soporte

Para problemas con actualizaciones:
- Revisar logs en `procesamiento_facturas_*.log`
- Reportar issue en GitHub
- Contactar al equipo de desarrollo
