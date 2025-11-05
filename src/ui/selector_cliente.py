"""
Ventana inicial para seleccionar el cliente (PyQt6)
"""

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from typing import Optional
import sys


class SelectorCliente(QMainWindow):
    """Ventana inicial para seleccionar el cliente"""

    def __init__(self):
        super().__init__()
        self.cliente_seleccionado = None
        self.setup_ui()
        self.centrar_ventana()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        window_geo = self.frameGeometry()
        center_point = screen.center()
        window_geo.moveCenter(center_point)
        self.move(window_geo.topLeft())

    def setup_ui(self):
        """Configura la interfaz de selección"""
        self.setWindowTitle("Procesador de Facturas - Selector de Cliente")
        self.setMinimumSize(800, 500)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        # Título
        titulo = QLabel("PROCESADOR DE FACTURAS ELECTRÓNICAS")
        titulo_font = QFont("Arial", 18, QFont.Weight.Bold)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(titulo)

        # Subtítulo
        subtitulo = QLabel("Seleccione el cliente que desea procesar:")
        subtitulo_font = QFont("Arial", 12)
        subtitulo.setFont(subtitulo_font)
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color: #34495e; padding: 5px;")
        main_layout.addWidget(subtitulo)

        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setFrameShadow(QFrame.Shadow.Sunken)
        separador.setStyleSheet("background-color: #bdc3c7;")
        main_layout.addWidget(separador)

        # Espaciador
        main_layout.addStretch()

        # Layout de botones
        botones_layout = QVBoxLayout()
        botones_layout.setSpacing(15)

        # Botón SEABOARD
        btn_seaboard = QPushButton("🌐 SEABOARD\nProcesamiento desde SharePoint/Local")
        btn_seaboard.setMinimumHeight(80)
        btn_seaboard.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        btn_seaboard.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        btn_seaboard.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_seaboard.clicked.connect(lambda: self.seleccionar_cliente("SEABOARD"))
        botones_layout.addWidget(btn_seaboard)

        # Botón CASA DEL AGRICULTOR
        btn_casa = QPushButton("🌾 CASA DEL AGRICULTOR\nProcesamiento desde archivos ZIP")
        btn_casa.setMinimumHeight(80)
        btn_casa.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        btn_casa.setStyleSheet("""
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
        btn_casa.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_casa.clicked.connect(lambda: self.seleccionar_cliente("CASA_DEL_AGRICULTOR"))
        botones_layout.addWidget(btn_casa)

        # Botón LACTALIS COMPRAS
        btn_lactalis = QPushButton("🥛 LACTALIS COMPRAS\nProcesamiento de facturas de compra")
        btn_lactalis.setMinimumHeight(80)
        btn_lactalis.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        btn_lactalis.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        btn_lactalis.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_lactalis.clicked.connect(lambda: self.seleccionar_cliente("LACTALIS_COMPRAS"))
        botones_layout.addWidget(btn_lactalis)

        main_layout.addLayout(botones_layout)

        # Espaciador
        main_layout.addStretch()

        # Información
        info_label = QLabel("💡 Cada cliente tiene su propio flujo de procesamiento optimizado")
        info_label.setFont(QFont("Arial", 9))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        main_layout.addWidget(info_label)

        # Botón Cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMaximumWidth(100)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cerrar.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        main_layout.addLayout(btn_layout)

    def seleccionar_cliente(self, cliente: str):
        """Guarda la selección y cierra la ventana"""
        self.cliente_seleccionado = cliente
        self.close()

    def ejecutar(self) -> Optional[str]:
        """Muestra el selector y retorna el cliente seleccionado"""
        self.show()
        return self.cliente_seleccionado
