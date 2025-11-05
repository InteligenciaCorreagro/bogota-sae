"""
Configuración de logging para la aplicación
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    """Configura el sistema de logging con rotación automática"""

    # Crear directorio de logs si no existe
    logs_dir = Path(__file__).parent.parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Archivo de log único con rotación
    log_file = logs_dir / 'procesamiento.log'

    # Configurar formato
    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

    # Handler con rotación (máximo 10MB por archivo, mantener 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Configurar logging raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger(__name__)
