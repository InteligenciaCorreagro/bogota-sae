@echo off
echo ====================================
echo Sistema SAE - Instalacion
echo ====================================
echo.
echo Instalando dependencias...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ====================================
echo Instalacion completada!
echo ====================================
echo.
echo Para iniciar el sistema, ejecute: INICIAR.bat
echo.
pause
