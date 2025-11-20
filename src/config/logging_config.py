"""
Configuración de logging para la aplicación
"""

import logging
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configura el sistema de logging"""
    # Crear carpeta logs si no existe
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)

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
