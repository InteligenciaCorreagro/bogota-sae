"""
Sistema de auto-actualización de la aplicación
Gestiona la verificación y descarga de nuevas versiones
"""

import json
import logging
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Tuple

from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from .version import __version__, VERSION_INFO

logger = logging.getLogger(__name__)


class DownloadThread(QThread):
    """Thread para descargar actualizaciones en segundo plano"""
    progress = pyqtSignal(int, int)  # bytes descargados, bytes totales
    finished = pyqtSignal(bool, str)  # success, message/path

    def __init__(self, url: str, destination: Path):
        super().__init__()
        self.url = url
        self.destination = destination

    def run(self):
        """Descarga el archivo mostrando progreso"""
        try:
            # Crear carpeta temporal si no existe
            self.destination.parent.mkdir(parents=True, exist_ok=True)

            # Descargar con progreso
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                self.progress.emit(downloaded, total_size)

            urllib.request.urlretrieve(self.url, self.destination, reporthook=report_progress)
            self.finished.emit(True, str(self.destination))

        except Exception as e:
            logger.error(f"Error descargando actualización: {str(e)}")
            self.finished.emit(False, f"Error al descargar: {str(e)}")


class Updater:
    """
    Sistema de auto-actualización

    Ejemplo de uso:
        updater = Updater(parent_widget)
        updater.check_for_updates(show_message_if_no_update=False)
    """

    def __init__(self, parent=None):
        """
        Inicializa el sistema de actualización

        Args:
            parent: Widget padre para mostrar diálogos (QWidget)
        """
        self.parent = parent
        self.current_version = __version__
        self.update_check_url = VERSION_INFO.get('update_check_url')
        self.download_url_base = VERSION_INFO.get('download_url_base')

    def check_for_updates(self, show_message_if_no_update: bool = True) -> Optional[Dict]:
        """
        Verifica si hay actualizaciones disponibles

        Args:
            show_message_if_no_update: Mostrar mensaje si no hay actualizaciones

        Returns:
            Dict con información de la actualización o None si no hay
        """
        try:
            # Descargar información de versión remota
            with urllib.request.urlopen(self.update_check_url, timeout=10) as response:
                version_data = json.loads(response.read().decode('utf-8'))

            remote_version = version_data.get('version', '0.0.0')

            # Comparar versiones
            if self._is_newer_version(remote_version, self.current_version):
                logger.info(f"Nueva versión disponible: {remote_version}")

                # Mostrar diálogo de actualización
                self._show_update_dialog(version_data)
                return version_data
            else:
                logger.info("La aplicación está actualizada")
                if show_message_if_no_update and self.parent:
                    QMessageBox.information(
                        self.parent,
                        "Sin actualizaciones",
                        f"Estás usando la versión más reciente ({self.current_version})"
                    )
                return None

        except urllib.error.URLError as e:
            logger.warning(f"No se pudo verificar actualizaciones (sin conexión): {str(e)}")
            if show_message_if_no_update and self.parent:
                QMessageBox.warning(
                    self.parent,
                    "Error de conexión",
                    "No se pudo verificar actualizaciones.\nVerifique su conexión a internet."
                )
            return None

        except Exception as e:
            logger.error(f"Error verificando actualizaciones: {str(e)}")
            if show_message_if_no_update and self.parent:
                QMessageBox.warning(
                    self.parent,
                    "Error",
                    f"Error al verificar actualizaciones:\n{str(e)}"
                )
            return None

    def _is_newer_version(self, remote: str, current: str) -> bool:
        """
        Compara versiones en formato semántico (X.Y.Z)

        Args:
            remote: Versión remota (ej: "2.1.0")
            current: Versión actual (ej: "2.0.0")

        Returns:
            True si la versión remota es más nueva
        """
        try:
            remote_parts = [int(x) for x in remote.split('.')]
            current_parts = [int(x) for x in current.split('.')]

            # Comparar parte por parte (major, minor, patch)
            for r, c in zip(remote_parts, current_parts):
                if r > c:
                    return True
                elif r < c:
                    return False

            return False

        except Exception as e:
            logger.error(f"Error comparando versiones: {str(e)}")
            return False

    def _show_update_dialog(self, version_data: Dict):
        """
        Muestra el diálogo de actualización disponible

        Args:
            version_data: Información de la versión remota
        """
        if not self.parent:
            return

        remote_version = version_data.get('version', 'Desconocida')
        release_notes = version_data.get('release_notes', 'Sin notas de versión')
        download_url = version_data.get('download_url', '')

        # Construir mensaje
        message = f"""
<h3>Nueva versión disponible: {remote_version}</h3>
<p><b>Versión actual:</b> {self.current_version}</p>

<h4>Novedades:</h4>
<p>{release_notes}</p>

<p>¿Desea descargar e instalar la actualización ahora?</p>
        """.strip()

        # Crear diálogo personalizado
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle("Actualización disponible")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

        # Mostrar diálogo
        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            self._download_and_install_update(download_url, remote_version)

    def _download_and_install_update(self, download_url: str, version: str):
        """
        Descarga e instala la actualización

        Args:
            download_url: URL del instalador
            version: Versión a descargar
        """
        if not download_url:
            QMessageBox.warning(
                self.parent,
                "Error",
                "No se encontró la URL de descarga"
            )
            return

        # Determinar nombre del archivo
        file_extension = '.exe' if sys.platform == 'win32' else '.tar.gz'
        temp_dir = Path(tempfile.gettempdir())
        download_path = temp_dir / f"bogota_sae_v{version}{file_extension}"

        # Crear diálogo de progreso
        progress_dialog = QProgressDialog(
            "Descargando actualización...",
            "Cancelar",
            0,
            100,
            self.parent
        )
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setWindowTitle("Descargando")
        progress_dialog.setAutoClose(False)

        # Crear thread de descarga
        download_thread = DownloadThread(download_url, download_path)

        # Conectar señales
        def update_progress(downloaded, total):
            if total > 0:
                percentage = int((downloaded / total) * 100)
                progress_dialog.setValue(percentage)
                progress_dialog.setLabelText(
                    f"Descargando actualización...\n"
                    f"{downloaded // (1024*1024)} MB / {total // (1024*1024)} MB"
                )

        def download_finished(success, message_or_path):
            progress_dialog.close()

            if success:
                self._install_update(Path(message_or_path), version)
            else:
                QMessageBox.critical(
                    self.parent,
                    "Error de descarga",
                    f"No se pudo descargar la actualización:\n{message_or_path}"
                )

        download_thread.progress.connect(update_progress)
        download_thread.finished.connect(download_finished)

        # Iniciar descarga
        download_thread.start()
        progress_dialog.exec()

        # Cancelar descarga si el usuario cierra el diálogo
        if progress_dialog.wasCanceled():
            download_thread.terminate()
            download_thread.wait()

    def _install_update(self, installer_path: Path, version: str):
        """
        Instala la actualización descargada

        Args:
            installer_path: Ruta al instalador descargado
            version: Versión descargada
        """
        if not installer_path.exists():
            QMessageBox.critical(
                self.parent,
                "Error",
                "No se encontró el archivo de actualización"
            )
            return

        # Mensaje de confirmación
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Instalar actualización")
        msg.setText(
            f"La actualización v{version} se descargó correctamente.\n\n"
            f"Para completar la instalación:\n"
            f"1. La aplicación se cerrará\n"
            f"2. Se ejecutará el instalador\n"
            f"3. Siga las instrucciones del instalador\n\n"
            f"¿Continuar con la instalación?"
        )
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                # Ejecutar instalador
                if sys.platform == 'win32':
                    # Windows: ejecutar .exe
                    subprocess.Popen([str(installer_path)])
                else:
                    # Linux/Mac: abrir en gestor de archivos
                    subprocess.Popen(['xdg-open', str(installer_path)])

                # Cerrar la aplicación
                logger.info(f"Iniciando instalación de v{version}. Cerrando aplicación...")
                sys.exit(0)

            except Exception as e:
                logger.error(f"Error al iniciar instalador: {str(e)}")
                QMessageBox.critical(
                    self.parent,
                    "Error",
                    f"No se pudo ejecutar el instalador:\n{str(e)}\n\n"
                    f"Ejecute manualmente:\n{installer_path}"
                )


# Ejemplo de archivo JSON remoto (version.json):
"""
{
    "version": "2.1.0",
    "build_date": "2025-12-01",
    "release_notes": "
        • Nueva funcionalidad de exportación masiva<br>
        • Mejoras de rendimiento en procesamiento XML<br>
        • Corrección de errores en módulo Lactalis
    ",
    "download_url": "https://github.com/tu-usuario/bogota-sae/releases/download/v2.1.0/BogotaSAE_v2.1.0_Setup.exe",
    "min_version_required": "2.0.0",
    "critical_update": false
}
"""
