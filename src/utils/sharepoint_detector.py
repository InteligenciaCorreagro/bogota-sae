"""
Detector de carpetas sincronizadas de SharePoint/OneDrive
"""

import os
import platform
from pathlib import Path
from typing import List


class DetectorSharePoint:
    """Detector de carpetas sincronizadas de SharePoint/OneDrive"""

    @staticmethod
    def encontrar_carpetas_sharepoint() -> List[Path]:
        """Encuentra carpetas de SharePoint/OneDrive sincronizadas en el sistema"""
        carpetas_encontradas = []

        if platform.system() == 'Windows':
            user_profile = Path(os.environ.get('USERPROFILE', ''))

            rutas_buscar = [
                user_profile / "OneDrive",
                user_profile / "OneDrive - SEABOARD",
                user_profile / "SharePoint",
                user_profile / "SEABOARD",
            ]

            drives = [f"{d}:\\" for d in "CDEFGHIJ" if os.path.exists(f"{d}:\\")]

            for drive in drives:
                drive_path = Path(drive)
                try:
                    for item in drive_path.iterdir():
                        if item.is_dir():
                            nombre_lower = item.name.lower()
                            if any(x in nombre_lower for x in ['sharepoint', 'onedrive', 'seaboard']):
                                rutas_buscar.append(item)
                except (PermissionError, OSError):
                    continue

            for ruta in rutas_buscar:
                if ruta.exists() and ruta.is_dir():
                    carpetas_encontradas.append(ruta)
                    try:
                        for subcarpeta in ruta.rglob("*"):
                            if subcarpeta.is_dir() and 'SEABOARD' in subcarpeta.name.upper():
                                carpetas_encontradas.append(subcarpeta)
                    except (PermissionError, OSError):
                        continue

        carpetas_unicas = []
        for carpeta in carpetas_encontradas:
            if carpeta not in carpetas_unicas:
                carpetas_unicas.append(carpeta)

        return carpetas_unicas
