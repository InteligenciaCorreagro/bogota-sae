"""
Sistema de auto-actualización de la aplicación
Verifica, descarga e instala actualizaciones automáticamente desde GitHub Releases
"""

import requests
import os
import sys
import zipfile
import shutil
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple
from packaging import version

from config.version import __version__, GITHUB_API_URL, AUTO_UPDATE_ENABLED

logger = logging.getLogger(__name__)


class AutoUpdater:
    """Gestor de actualizaciones automáticas"""

    def __init__(self):
        self.current_version = __version__
        self.latest_version = None
        self.download_url = None
        self.is_frozen = getattr(sys, 'frozen', False)

        # Determinar la ruta base de la aplicación
        if self.is_frozen:
            # Si es ejecutable, obtener el directorio del .exe
            self.app_path = Path(sys.executable).parent
        else:
            # Si es script, obtener el directorio raíz del proyecto
            self.app_path = Path(__file__).parent.parent.parent

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verifica si hay actualizaciones disponibles

        Returns:
            Tuple[bool, str, str]: (hay_actualización, versión_nueva, notas_versión)
        """
        if not AUTO_UPDATE_ENABLED:
            logger.info("Auto-actualización deshabilitada")
            return False, None, None

        try:
            logger.info(f"Verificando actualizaciones... Versión actual: {self.current_version}")

            # Obtener información de la última release desde GitHub
            response = requests.get(GITHUB_API_URL, timeout=10)
            response.raise_for_status()

            release_data = response.json()

            # Extraer información de la release
            self.latest_version = release_data.get('tag_name', '').lstrip('v')
            release_notes = release_data.get('body', 'Sin notas de versión')

            # Buscar el asset ejecutable de Windows
            assets = release_data.get('assets', [])
            for asset in assets:
                name = asset.get('name', '')
                if name.endswith('.exe') or name.endswith('.zip'):
                    self.download_url = asset.get('browser_download_url')
                    break

            if not self.download_url:
                logger.warning("No se encontró ejecutable en la release")
                return False, None, None

            # Comparar versiones
            if version.parse(self.latest_version) > version.parse(self.current_version):
                logger.info(f"Nueva versión disponible: {self.latest_version}")
                return True, self.latest_version, release_notes
            else:
                logger.info("La aplicación está actualizada")
                return False, None, None

        except requests.RequestException as e:
            logger.error(f"Error al verificar actualizaciones: {e}")
            return False, None, None
        except Exception as e:
            logger.error(f"Error inesperado al verificar actualizaciones: {e}")
            return False, None, None

    def download_update(self, progress_callback=None) -> Optional[Path]:
        """
        Descarga la actualización

        Args:
            progress_callback: Función callback(bytes_descargados, total_bytes)

        Returns:
            Path del archivo descargado o None si falla
        """
        if not self.download_url:
            logger.error("No hay URL de descarga disponible")
            return None

        try:
            # Crear directorio temporal
            temp_dir = Path(tempfile.gettempdir()) / "reggis_update"
            temp_dir.mkdir(exist_ok=True)

            # Nombre del archivo
            filename = Path(self.download_url).name
            temp_file = temp_dir / filename

            logger.info(f"Descargando actualización desde: {self.download_url}")

            # Descargar con progress
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            logger.info(f"Actualización descargada en: {temp_file}")
            return temp_file

        except Exception as e:
            logger.error(f"Error al descargar actualización: {e}")
            return None

    def install_update(self, update_file: Path) -> bool:
        """
        Instala la actualización descargada

        Args:
            update_file: Path del archivo de actualización

        Returns:
            True si se instaló correctamente, False si falló
        """
        try:
            logger.info(f"Instalando actualización desde: {update_file}")

            if update_file.suffix == '.exe':
                # Es un ejecutable, reemplazar el actual
                return self._install_exe(update_file)
            elif update_file.suffix == '.zip':
                # Es un ZIP, extraer y reemplazar
                return self._install_zip(update_file)
            else:
                logger.error(f"Formato de actualización no soportado: {update_file.suffix}")
                return False

        except Exception as e:
            logger.error(f"Error al instalar actualización: {e}")
            return False

    def _install_exe(self, exe_file: Path) -> bool:
        """Instala actualización desde ejecutable"""
        try:
            if not self.is_frozen:
                logger.warning("No se puede actualizar ejecutable en modo desarrollo")
                return False

            # Crear script de actualización que se ejecutará después de cerrar la app
            update_script = self.app_path / "update.bat"
            current_exe = Path(sys.executable)
            backup_exe = current_exe.with_suffix('.exe.old')

            script_content = f"""@echo off
echo Actualizando aplicacion...
timeout /t 2 /nobreak >nul
taskkill /F /IM "{current_exe.name}" >nul 2>&1
timeout /t 1 /nobreak >nul
move /Y "{current_exe}" "{backup_exe}" >nul 2>&1
move /Y "{exe_file}" "{current_exe}" >nul
if exist "{backup_exe}" del "{backup_exe}"
start "" "{current_exe}"
del "%~f0"
"""

            with open(update_script, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # Ejecutar script de actualización y cerrar la aplicación
            subprocess.Popen(['cmd', '/c', str(update_script)],
                           creationflags=subprocess.CREATE_NO_WINDOW)

            logger.info("Script de actualización iniciado")
            return True

        except Exception as e:
            logger.error(f"Error al instalar EXE: {e}")
            return False

    def _install_zip(self, zip_file: Path) -> bool:
        """Instala actualización desde ZIP"""
        try:
            # Extraer ZIP a directorio temporal
            extract_dir = zip_file.parent / "extracted"
            extract_dir.mkdir(exist_ok=True)

            logger.info(f"Extrayendo {zip_file} a {extract_dir}")

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Buscar el ejecutable en el directorio extraído
            exe_files = list(extract_dir.rglob("*.exe"))

            if not exe_files:
                logger.error("No se encontró ejecutable en el ZIP")
                return False

            # Usar el primer ejecutable encontrado
            exe_file = exe_files[0]
            return self._install_exe(exe_file)

        except Exception as e:
            logger.error(f"Error al instalar ZIP: {e}")
            return False

    def cleanup_old_files(self):
        """Limpia archivos antiguos de actualizaciones"""
        try:
            # Limpiar archivos .old
            for old_file in self.app_path.glob("*.old"):
                try:
                    old_file.unlink()
                    logger.info(f"Eliminado archivo antiguo: {old_file}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar {old_file}: {e}")

            # Limpiar directorio temporal de actualizaciones
            temp_dir = Path(tempfile.gettempdir()) / "reggis_update"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            logger.warning(f"Error al limpiar archivos antiguos: {e}")

    def auto_update(self, progress_callback=None) -> bool:
        """
        Proceso completo de auto-actualización

        Args:
            progress_callback: Función callback para reportar progreso

        Returns:
            True si se inició la actualización, False si no
        """
        # Verificar si hay actualización
        has_update, new_version, notes = self.check_for_updates()

        if not has_update:
            return False

        logger.info(f"Iniciando auto-actualización a versión {new_version}")

        # Descargar actualización
        update_file = self.download_update(progress_callback)

        if not update_file:
            logger.error("Fallo la descarga de la actualización")
            return False

        # Instalar actualización
        success = self.install_update(update_file)

        if success:
            logger.info("Actualización instalada correctamente")
            # La aplicación se cerrará automáticamente
            return True
        else:
            logger.error("Fallo la instalación de la actualización")
            return False


# Función de conveniencia
def check_and_update(show_message_callback=None, progress_callback=None) -> bool:
    """
    Verifica y actualiza la aplicación si hay una nueva versión

    Args:
        show_message_callback: Función para mostrar mensajes al usuario
        progress_callback: Función para reportar progreso de descarga

    Returns:
        True si se inició una actualización, False si no
    """
    updater = AutoUpdater()

    # Verificar actualizaciones
    has_update, new_version, notes = updater.check_for_updates()

    if has_update and show_message_callback:
        # Preguntar al usuario si quiere actualizar
        message = f"Nueva versión disponible: {new_version}\n\n{notes}\n\n¿Desea actualizar ahora?"
        if not show_message_callback(message):
            return False
    elif not has_update:
        return False

    # Realizar actualización
    return updater.auto_update(progress_callback)
