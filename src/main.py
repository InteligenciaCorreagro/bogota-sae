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
from PyQt6.QtWidgets import QApplication, QMessageBox

from config.logging_config import setup_logging
from ui.selector_cliente import SelectorCliente
from ui.interfaz_unificada import InterfazUnificada

# Configurar logging
logger = setup_logging()


def main():
    """Función principal que inicia la aplicación y permite volver al selector"""
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle("Fusion")

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
