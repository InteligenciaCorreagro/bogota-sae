#!/usr/bin/env python
"""
Script para ejecutar el Procesador de Facturas Electrónicas
Ejecuta la aplicación desde cualquier ubicación
"""

import sys
from pathlib import Path

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importar y ejecutar la aplicación
if __name__ == "__main__":
    from main import main
    main()
