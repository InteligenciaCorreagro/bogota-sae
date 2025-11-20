"""
Módulo de tabs para la interfaz con PyQt6
Cada tab representa una funcionalidad principal de la aplicación
"""

from .tab_seaboard import TabSeaboard
from .tab_casa_agricultor import TabCasaAgricultor
from .tab_lactalis_compras import TabLactalisCompras

__all__ = [
    'TabSeaboard',
    'TabCasaAgricultor',
    'TabLactalisCompras'
]
