"""
Tab para procesamiento de facturas CASA DEL AGRICULTOR
Procesa archivos ZIP con XML embebido
"""

import os
import platform
import logging
from pathlib import Path

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QProgressBar, QFileDialog,
                              QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from processors.casa_del_agricultor_processor import ProcesadorCasaDelAgricultor
from config.constants import get_data_output_path

logger = logging.getLogger(__name__)


class ProcesamientoThread(QThread):
    """Thread para ejecutar procesamiento en segundo plano"""
    finished = pyqtSignal(bool, str, object)  # success, message, result

    def __init__(self, procesador_func, *args):
        super().__init__()
        self.procesador_func = procesador_func
        self.args = args

    def run(self):
        try:
            result = self.procesador_func(*self.args)
            self.finished.emit(True, "Proceso completado exitosamente", result)
        except Exception as e:
            logger.error(f"Error en procesamiento: {str(e)}", exc_info=True)
            self.finished.emit(False, f"Error: {str(e)}", None)


class TabCasaAgricultor(QWidget):
    """
    Tab para procesamiento de facturas CASA DEL AGRICULTOR

    Funcionalidades:
    - Selección de carpeta con archivos ZIP
    - Extracción automática de XML desde ZIP
    - Conversión de unidades (LBR → KG, GRAMOS → KG)
    - Parsing de CDATA en XML
    - Procesamiento en segundo plano
    """

    def __init__(self):
        super().__init__()
        self.carpeta_entrada = None
        self.procesamiento_thread = None

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del tab"""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Título ---
        titulo = QLabel("🌾 PROCESADOR CASA DEL AGRICULTOR")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #27ae60; padding: 10px;")
        main_layout.addWidget(titulo)

        # --- Descripción ---
        descripcion = QLabel(
            "Procesa archivos ZIP que contienen facturas electrónicas XML.\n"
            "Soporta conversión de unidades (LBR → KG, GRAMOS → KG) y parsing de CDATA."
        )
        descripcion.setFont(QFont("Arial", 9))
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        descripcion.setStyleSheet("color: #555; padding: 5px;")
        descripcion.setWordWrap(True)
        main_layout.addWidget(descripcion)

        # --- Group Box: Selección de Archivos ---
        group_archivos = QGroupBox("Seleccionar Archivos ZIP")
        group_archivos.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)

        # Información
        info_label = QLabel(
            "ℹ️ Seleccione la carpeta que contiene los archivos ZIP de facturas.\n"
            "Cada archivo ZIP debe contener los XML de las facturas."
        )
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet("color: #34495e; padding: 5px;")
        info_label.setWordWrap(True)
        group_layout.addWidget(info_label)

        # Botón seleccionar carpeta
        btn_seleccionar = QPushButton("📦 SELECCIONAR CARPETA CON ARCHIVOS ZIP")
        btn_seleccionar.setMinimumHeight(60)
        btn_seleccionar.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn_seleccionar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
            QPushButton:pressed {
                background-color: #196f3d;
            }
        """)
        btn_seleccionar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_seleccionar.clicked.connect(self.seleccionar_carpeta)
        group_layout.addWidget(btn_seleccionar)

        group_archivos.setLayout(group_layout)
        main_layout.addWidget(group_archivos)

        # --- Barra de Progreso ---
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)  # Modo indeterminado
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
            }
        """)
        main_layout.addWidget(self.progress)

        # --- Label de Estado ---
        self.estado_label = QLabel("")
        self.estado_label.setFont(QFont("Arial", 10))
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.estado_label.setStyleSheet("padding: 10px;")
        main_layout.addWidget(self.estado_label)

        # Espaciador
        main_layout.addStretch()

        # --- Información adicional ---
        info_footer = QLabel(
            "💡 Los archivos se descomprimirán automáticamente y se procesarán en formato REGGIS.\n"
            "Los resultados se guardarán en la carpeta 'Resultados_CASA_DEL_AGRICULTOR'."
        )
        info_footer.setFont(QFont("Arial", 8))
        info_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_footer.setStyleSheet("color: #7f8c8d; padding: 10px;")
        info_footer.setWordWrap(True)
        main_layout.addWidget(info_footer)

        self.setLayout(main_layout)

    def seleccionar_carpeta(self):
        """Permite seleccionar una carpeta con archivos ZIP"""
        carpeta = QFileDialog.getExistingDirectory(
            self,
            "Seleccione la carpeta con archivos ZIP",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if not carpeta:
            return

        self.carpeta_entrada = Path(carpeta)

        # Buscar archivos ZIP
        zip_files = list(self.carpeta_entrada.glob("*.zip"))

        if not zip_files:
            QMessageBox.critical(
                self,
                "Sin archivos",
                "No se encontraron archivos ZIP en la carpeta seleccionada"
            )
            return

        # Confirmar procesamiento
        respuesta = QMessageBox.question(
            self,
            "Confirmar procesamiento",
            f"Se encontraron {len(zip_files)} archivo(s) ZIP.\n\n"
            f"Carpeta: {self.carpeta_entrada.name}\n\n"
            f"¿Procesar ahora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.iniciar_procesamiento()

    def iniciar_procesamiento(self):
        """Inicia el procesamiento en segundo plano"""
        self.progress.setVisible(True)
        self.estado_label.setText("⏳ Procesando archivos ZIP de CASA DEL AGRICULTOR...")
        self.estado_label.setStyleSheet("color: #f39c12; padding: 10px; font-weight: bold;")

        # Crear carpeta de salida usando estructura data/YYYY-MM-DD/
        carpeta_salida = get_data_output_path()

        # Crear procesador
        procesador = ProcesadorCasaDelAgricultor(self.carpeta_entrada, carpeta_salida)

        # Iniciar thread de procesamiento
        self.procesamiento_thread = ProcesamientoThread(procesador.procesar)
        self.procesamiento_thread.finished.connect(self.procesamiento_finalizado)
        self.procesamiento_thread.start()

    def procesamiento_finalizado(self, success: bool, message: str, result):
        """
        Callback cuando el procesamiento termina

        Args:
            success: True si fue exitoso
            message: Mensaje de resultado
            result: Path de carpeta de resultados o None
        """
        self.progress.setVisible(False)

        if success:
            self.estado_label.setText("✅ Proceso completado exitosamente")
            self.estado_label.setStyleSheet("color: #27ae60; padding: 10px; font-weight: bold;")

            respuesta = QMessageBox.question(
                self,
                "Éxito",
                f"{message}\n\n"
                f"📂 Archivos guardados en:\n{result.name}\n\n"
                f"¿Desea abrir la carpeta de resultados?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                self.abrir_carpeta(result)
        else:
            self.estado_label.setText("❌ Error en el procesamiento")
            self.estado_label.setStyleSheet("color: #e74c3c; padding: 10px; font-weight: bold;")
            QMessageBox.critical(
                self,
                "Error de procesamiento",
                f"Ocurrió un error durante el procesamiento:\n\n{message}"
            )

    def abrir_carpeta(self, carpeta: Path):
        """
        Abre la carpeta de resultados en el explorador del sistema

        Args:
            carpeta: Path a la carpeta a abrir
        """
        try:
            if platform.system() == 'Windows':
                os.startfile(carpeta)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{carpeta}"')
            else:  # Linux
                os.system(f'xdg-open "{carpeta}"')
        except Exception as e:
            logger.error(f"Error abriendo carpeta: {str(e)}")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo abrir la carpeta automáticamente:\n{str(e)}\n\n"
                f"Ubicación: {carpeta}"
            )
