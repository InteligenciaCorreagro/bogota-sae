"""
Procesador Unificado de Facturas Electrónicas XML a Excel
Sistema Multi-Cliente: SEABOARD, CASA DEL AGRICULTOR y LACTALIS COMPRAS
Autor: Sistema REGGIS

Punto de entrada principal de la aplicación
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

import logging
from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt

from config.logging_config import setup_logging
from config.version import __version__, CHECK_UPDATE_ON_STARTUP, APP_NAME
from ui.selector_cliente import SelectorCliente
from ui.interfaz_unificada import InterfazUnificada
from utils.auto_updater import AutoUpdater

# Configurar logging
logger = setup_logging()


def check_for_updates_on_startup(app):
    """Verifica actualizaciones al iniciar la aplicación"""
    if not CHECK_UPDATE_ON_STARTUP:
        return

    try:
        logger.info("Verificando actualizaciones al inicio...")
        updater = AutoUpdater()

        # Verificar si hay actualizaciones
        has_update, new_version, notes = updater.check_for_updates()

        if has_update:
            # Mostrar diálogo de actualización
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Actualización Disponible")
            msg.setText(f"<h3>Nueva versión disponible: {new_version}</h3>")
            msg.setInformativeText(
                f"Versión actual: {__version__}\n"
                f"Nueva versión: {new_version}\n\n"
                f"Notas de la versión:\n{notes[:200]}..."
            )
            msg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            msg.setDefaultButton(QMessageBox.StandardButton.Yes)
            msg.button(QMessageBox.StandardButton.Yes).setText("Actualizar Ahora")
            msg.button(QMessageBox.StandardButton.No).setText("Más Tarde")

            response = msg.exec()

            if response == QMessageBox.StandardButton.Yes:
                # Crear diálogo de progreso
                progress = QProgressDialog(
                    "Descargando actualización...",
                    "Cancelar",
                    0,
                    100
                )
                progress.setWindowTitle("Actualizando...")
                progress.setWindowModality(Qt.WindowModality.ApplicationModal)
                progress.setMinimumDuration(0)
                progress.show()

                def update_progress(downloaded, total):
                    if total > 0:
                        percent = int((downloaded / total) * 100)
                        progress.setValue(percent)
                    app.processEvents()

                # Descargar actualización
                update_file = updater.download_update(update_progress)

                if update_file:
                    progress.close()

                    # Instalar actualización
                    success = updater.install_update(update_file)

                    if success:
                        QMessageBox.information(
                            None,
                            "Actualización Exitosa",
                            "La actualización se instalará al cerrar la aplicación.\n"
                            "La aplicación se reiniciará automáticamente."
                        )
                        # La aplicación se cerrará y reiniciará automáticamente
                        sys.exit(0)
                    else:
                        QMessageBox.critical(
                            None,
                            "Error de Actualización",
                            "No se pudo instalar la actualización.\n"
                            "Intente descargar manualmente desde el repositorio."
                        )
                else:
                    progress.close()
                    QMessageBox.critical(
                        None,
                        "Error de Descarga",
                        "No se pudo descargar la actualización.\n"
                        "Verifique su conexión a internet."
                    )

    except Exception as e:
        logger.warning(f"Error al verificar actualizaciones: {e}")
        # No mostrar error al usuario, solo registrar en log


def main():
    """Función principal que inicia la aplicación y permite volver al selector"""
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle("Fusion")

    # Verificar actualizaciones al inicio
    check_for_updates_on_startup(app)

    try:
        while True:
            selector = SelectorCliente()
            selector.show()
            app.exec()

            cliente = selector.cliente_seleccionado

            if not cliente:
                logger.info("No se seleccionó ningún cliente. Aplicación cerrada.")
                break

            logger.info(f"Cliente seleccionado: {cliente}")

            interfaz = InterfazUnificada(cliente, app)
            interfaz.show()
            app.exec()

            if getattr(interfaz, "request_return", False):
                # Volver al selector
                continue
            else:
                # Salir de la aplicación
                break

    except Exception as e:
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error Fatal")
            msg.setText(f"Error al iniciar:\n\n{str(e)}")
            msg.exec()
        except:
            pass
        logger.error(f"Error fatal: {str(e)}", exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
