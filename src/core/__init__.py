"""
Módulo core con lógica de negocio centralizada
"""

from .version import __version__, APP_NAME, VERSION_INFO
from .updater import Updater

__all__ = ['__version__', 'APP_NAME', 'VERSION_INFO', 'Updater']
