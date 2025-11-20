#!/usr/bin/env python
"""
Procesador de Facturas Electrónicas REGGIS
Punto de entrada principal de la aplicación

Este archivo inicia la aplicación con la nueva interfaz de tabs.
Para ejecutar: python app.py
"""

import sys
import logging
from pathlib import Path

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from config.logging_config import setup_logging
from core.version import get_version_string
from ui.main_window import MainWindow

# Configurar logging
logger = setup_logging()


def main():
    """
    Función principal de la aplicación

    Inicia la aplicación PyQt6 con la ventana principal de tabs
    """
    logger.info("=" * 80)
    logger.info(f"Iniciando {get_version_string()}")
    logger.info("=" * 80)

    # Crear aplicación Qt
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle("Fusion")

    # Configurar propiedades de la aplicación
    app.setApplicationName("Procesador de Facturas REGGIS")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Sistema REGGIS")

    try:
        # Crear y mostrar ventana principal
        ventana = MainWindow()
        ventana.show()

        logger.info("Aplicación iniciada exitosamente")

        # Iniciar loop de eventos
        exit_code = app.exec()

        logger.info(f"Aplicación cerrada con código: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        # Manejo de errores críticos
        logger.error(f"Error fatal al iniciar la aplicación: {str(e)}", exc_info=True)

        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error Fatal")
            msg.setText(
                f"Error al iniciar la aplicación:\n\n{str(e)}\n\n"
                f"Consulte los logs para más detalles."
            )
            msg.setDetailedText(
                f"Tipo de error: {type(e).__name__}\n"
                f"Mensaje: {str(e)}\n\n"
                f"Verifique:\n"
                f"1. Que todas las dependencias están instaladas (pip install -r requirements.txt)\n"
                f"2. Que PyQt6 está correctamente instalado\n"
                f"3. Los logs en el directorio actual para más información"
            )
            msg.exec()
        except:
            # Si falla el diálogo, imprimir en consola
            print(f"ERROR FATAL: {str(e)}")

        sys.exit(1)


if __name__ == "__main__":
    main()
