"""
Sistema de Actualización Automática desde GitHub
Autor: Sistema REGGIS
"""

import sys
import os
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import logging

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)

# Configuración del repositorio
GITHUB_REPO = "InteligenciaCorreagro/bogota-sae"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}"
VERSION_FILE = "version.json"


class AutoUpdater:
    """Gestor de actualizaciones automáticas desde GitHub"""

    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.version_file = self.current_dir / VERSION_FILE
        self.current_version = self.get_current_version()

    def get_current_version(self) -> str:
        """Obtiene la versión actual del sistema"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '1.0.0')
        except Exception as e:
            logger.error(f"Error al leer versión actual: {e}")

        return "1.0.0"

    def save_version(self, version: str):
        """Guarda la versión actual"""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': version,
                    'last_updated': self.get_current_datetime()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar versión: {e}")

    def get_current_datetime(self) -> str:
        """Retorna la fecha y hora actual en formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verifica si hay actualizaciones disponibles en GitHub

        Returns:
            Tuple[bool, Optional[str], Optional[str]]:
                (hay_actualizacion, version_nueva, mensaje_error)
        """
        if requests is None:
            return False, None, "Módulo 'requests' no disponible"

        try:
            # Obtener el último commit de la rama main
            response = requests.get(
                f"{GITHUB_API_URL}/branches/main",
                timeout=10
            )

            if response.status_code != 200:
                return False, None, f"Error al consultar GitHub: {response.status_code}"

            data = response.json()
            latest_sha = data['commit']['sha'][:7]  # Primeros 7 caracteres del SHA

            # Obtener información del último commit para la versión
            commit_response = requests.get(
                f"{GITHUB_API_URL}/commits/{data['commit']['sha']}",
                timeout=10
            )

            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                commit_date = commit_data['commit']['committer']['date'][:10]
                latest_version = f"{commit_date}-{latest_sha}"
            else:
                latest_version = latest_sha

            # Comparar versiones
            if latest_version != self.current_version:
                return True, latest_version, None

            return False, None, None

        except requests.exceptions.Timeout:
            return False, None, "Timeout al conectar con GitHub"
        except requests.exceptions.ConnectionError:
            return False, None, "No se pudo conectar con GitHub"
        except Exception as e:
            return False, None, f"Error inesperado: {str(e)}"

    def download_update(self, branch: str = "main") -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Descarga la última versión desde GitHub

        Returns:
            Tuple[bool, Optional[Path], Optional[str]]:
                (exito, ruta_temp, mensaje_error)
        """
        if requests is None:
            return False, None, "Módulo 'requests' no disponible"

        try:
            # Crear directorio temporal
            temp_dir = Path(tempfile.mkdtemp(prefix="sae_update_"))

            # Descargar archivos principales
            files_to_download = [
                "unified_invoice_processor.py",
                "requirements.txt",
                "version.json",
                "auto_updater.py"
            ]

            logger.info("Descargando actualización desde GitHub...")

            for file_name in files_to_download:
                url = f"{GITHUB_RAW_URL}/{branch}/{file_name}"
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    file_path = temp_dir / file_name
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Descargado: {file_name}")
                else:
                    logger.warning(f"No se pudo descargar: {file_name} (código {response.status_code})")

            return True, temp_dir, None

        except Exception as e:
            return False, None, f"Error al descargar actualización: {str(e)}"

    def apply_update(self, temp_dir: Path) -> Tuple[bool, Optional[str]]:
        """
        Aplica la actualización descargada

        Returns:
            Tuple[bool, Optional[str]]: (exito, mensaje_error)
        """
        try:
            # Crear backup
            backup_dir = self.current_dir / "backup"
            backup_dir.mkdir(exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            files_to_backup = [
                "unified_invoice_processor.py",
                "auto_updater.py",
                "version.json"
            ]

            # Hacer backup de archivos existentes
            for file_name in files_to_backup:
                src = self.current_dir / file_name
                if src.exists():
                    dst = backup_dir / f"{file_name}.{timestamp}.bak"
                    shutil.copy2(src, dst)
                    logger.info(f"Backup creado: {dst.name}")

            # Copiar nuevos archivos
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    dst = self.current_dir / file_path.name
                    shutil.copy2(file_path, dst)
                    logger.info(f"Actualizado: {file_path.name}")

            # Actualizar versión
            version_file_temp = temp_dir / VERSION_FILE
            if version_file_temp.exists():
                with open(version_file_temp, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    new_version = version_data.get('version', 'unknown')
                    self.save_version(new_version)

            # Limpiar directorio temporal
            shutil.rmtree(temp_dir, ignore_errors=True)

            return True, None

        except Exception as e:
            return False, f"Error al aplicar actualización: {str(e)}"

    def install_requirements(self) -> Tuple[bool, Optional[str]]:
        """
        Instala las dependencias necesarias desde requirements.txt

        Returns:
            Tuple[bool, Optional[str]]: (exito, mensaje_error)
        """
        requirements_file = self.current_dir / "requirements.txt"

        if not requirements_file.exists():
            return False, "Archivo requirements.txt no encontrado"

        try:
            logger.info("Instalando dependencias...")

            # Usar pip para instalar requirements
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "--quiet"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                logger.info("Dependencias instaladas correctamente")
                return True, None
            else:
                error_msg = result.stderr or "Error desconocido al instalar dependencias"
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Timeout al instalar dependencias"
        except Exception as e:
            return False, f"Error al instalar dependencias: {str(e)}"

    def perform_full_update(self) -> Tuple[bool, Optional[str]]:
        """
        Realiza el proceso completo de actualización

        Returns:
            Tuple[bool, Optional[str]]: (exito, mensaje_error)
        """
        # Verificar actualizaciones
        has_update, new_version, error = self.check_for_updates()

        if error:
            return False, error

        if not has_update:
            return False, "No hay actualizaciones disponibles"

        logger.info(f"Nueva versión disponible: {new_version}")

        # Descargar actualización
        success, temp_dir, error = self.download_update()

        if not success:
            return False, error

        # Aplicar actualización
        success, error = self.apply_update(temp_dir)

        if not success:
            return False, error

        # Instalar dependencias
        success, error = self.install_requirements()

        if not success:
            logger.warning(f"Advertencia al instalar dependencias: {error}")
            # No falla la actualización si hay problemas con dependencias

        return True, None


def check_and_notify_update() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Función auxiliar para verificar actualizaciones

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            (hay_actualizacion, version_nueva, mensaje_error)
    """
    updater = AutoUpdater()
    return updater.check_for_updates()


def perform_update() -> Tuple[bool, Optional[str]]:
    """
    Función auxiliar para realizar actualización completa

    Returns:
        Tuple[bool, Optional[str]]: (exito, mensaje_error)
    """
    updater = AutoUpdater()
    return updater.perform_full_update()


if __name__ == "__main__":
    # Prueba del sistema de actualización
    logging.basicConfig(level=logging.INFO)

    print("=== Sistema de Actualización SAE ===")
    print(f"Versión actual: {AutoUpdater().current_version}")

    print("\nVerificando actualizaciones...")
    has_update, new_version, error = check_and_notify_update()

    if error:
        print(f"Error: {error}")
    elif has_update:
        print(f"¡Nueva versión disponible!: {new_version}")

        response = input("\n¿Desea actualizar ahora? (s/n): ")
        if response.lower() == 's':
            success, error = perform_update()
            if success:
                print("\n¡Actualización completada exitosamente!")
                print("Por favor, reinicie la aplicación.")
            else:
                print(f"\nError en la actualización: {error}")
    else:
        print("El sistema está actualizado.")
