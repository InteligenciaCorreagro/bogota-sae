"""
Configuración de logging para la aplicación
"""

import logging
from datetime import datetime
from .constants import get_logs_dir

def setup_logging():
    """Configura el sistema de logging"""
    # Obtener carpeta logs en ubicación apropiada según el sistema operativo
    logs_dir = get_logs_dir()

    log_file = logs_dir / f'procesamiento_facturas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
