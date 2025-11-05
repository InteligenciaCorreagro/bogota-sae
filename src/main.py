"""
Procesador Unificado de Facturas Electrónicas XML a Excel
Sistema Multi-Cliente: SEABOARD y CASA DEL AGRICULTOR
Autor: Sistema REGGIS

Punto de entrada principal de la aplicación
"""

import logging
from tkinter import messagebox

from config.logging_config import setup_logging
from ui.selector_cliente import SelectorCliente
from ui.interfaz_unificada import InterfazUnificada

# Configurar logging
logger = setup_logging()


def main():
    """Función principal que inicia la aplicación y permite volver al selector"""
    try:
        while True:
            selector = SelectorCliente()
            cliente = selector.ejecutar()

            if not cliente:
                logger.info("No se seleccionó ningún cliente. Aplicación cerrada.")
                break

            logger.info(f"Cliente seleccionado: {cliente}")

            app = InterfazUnificada(cliente)
            app.ejecutar()

            if getattr(app, "request_return", False):
                continue
            else:
                break

    except Exception as e:
        try:
            messagebox.showerror("Error Fatal", f"Error al iniciar:\n\n{str(e)}")
        except:
            pass
        logger.error(f"Error fatal: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
