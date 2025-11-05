"""
Configuración de logging para la aplicación
"""

import logging
from datetime import datetime

def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                f'procesamiento_facturas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            ),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
