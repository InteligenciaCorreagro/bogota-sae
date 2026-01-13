"""
Ventana principal de la aplicación con interfaz de tabs (QTabWidget)
Arquitectura moderna con separación clara de funcionalidades
"""

import sys
import logging
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                              QMenuBar, QMenu, QMessageBox, QApplication,
                              QStatusBar, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon

from core.version import __version__, APP_NAME, get_version_string
from core.updater import Updater
from ui.tabs import TabCasaAgricultor, TabSeaboard, TabLactalisCompras, TabLactalisVentas

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación

    Características:
    - Interfaz con tabs para diferentes clientes
    - Menú de navegación completo
    - Sistema de auto-actualización integrado
    - Barra de estado con información de versión
    - Diseño moderno y responsive
    """

    def __init__(self):
        super().__init__()
        self.updater = Updater(self)
        self.setup_ui()
        self.centrar_ventana()

        # Verificar actualizaciones al iniciar (sin mostrar mensaje si no hay)
        QTimer.singleShot(2000, lambda: self.updater.check_for_updates(show_message_if_no_update=False))

    def setup_ui(self):
        """Configura la interfaz principal de la ventana"""
        # Configuración de ventana
        self.setWindowTitle(get_version_string())
        self.setMinimumSize(1000, 700)

        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # --- Header ---
        header_widget = self.crear_header()
        main_layout.addWidget(header_widget)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Arial", 10))
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #0078D4;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
        """)

        # Crear y agregar tabs
        self.tab_seaboard = TabSeaboard()
        self.tab_casa = TabCasaAgricultor()
        self.tab_lactalis_compras = TabLactalisCompras()
        self.tab_lactalis_ventas = TabLactalisVentas()

        self.tab_widget.addTab(self.tab_seaboard, "🌐 SEABOARD")
        self.tab_widget.addTab(self.tab_casa, "🌾 CASA DEL AGRICULTOR")
        self.tab_widget.addTab(self.tab_lactalis_compras, "🥛 LACTALIS COMPRAS")
        self.tab_widget.addTab(self.tab_lactalis_ventas, "💰 LACTALIS VENTAS")

        main_layout.addWidget(self.tab_widget)

        # --- Menú ---
        self.crear_menu()

        # --- Barra de Estado ---
        self.crear_status_bar()

    def crear_header(self) -> QWidget:
        """
        Crea el header de la aplicación con título y logo

        Returns:
            QWidget con el header
        """
        header = QWidget()
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #0078D4, stop:1 #005a9e);
        """)
        header.setMinimumHeight(80)
        header.setMaximumHeight(80)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)

        # Título
        titulo = QLabel(APP_NAME)
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        titulo.setStyleSheet("color: white;")

        # Versión
        version = QLabel(f"v{__version__}")
        version.setFont(QFont("Arial", 10))
        version.setStyleSheet("color: #ecf0f1;")

        layout.addWidget(titulo)
        layout.addStretch()
        layout.addWidget(version)

        header.setLayout(layout)
        return header

    def crear_menu(self):
        """Crea el menú principal de la aplicación"""
        menubar = self.menuBar()
        menubar.setFont(QFont("Arial", 9))

        # --- Menú Archivo ---
        menu_archivo = menubar.addMenu("&Archivo")

        # Acción: Salir
        accion_salir = QAction("&Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.setStatusTip("Cerrar la aplicación")
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

        # --- Menú Herramientas ---
        menu_herramientas = menubar.addMenu("&Herramientas")

        # Acción: Buscar actualizaciones
        accion_actualizar = QAction("Buscar &Actualizaciones", self)
        accion_actualizar.setStatusTip("Verificar si hay actualizaciones disponibles")
        accion_actualizar.triggered.connect(self.verificar_actualizaciones)
        menu_herramientas.addAction(accion_actualizar)

        menu_herramientas.addSeparator()

        # Acción: Abrir carpeta de logs
        accion_logs = QAction("Abrir carpeta de &Logs", self)
        accion_logs.setStatusTip("Abrir la carpeta con archivos de log")
        accion_logs.triggered.connect(self.abrir_carpeta_logs)
        menu_herramientas.addAction(accion_logs)

        # Acción: Borrar logs
        accion_borrar_logs = QAction("&Borrar archivos de logs", self)
        accion_borrar_logs.setStatusTip("Eliminar todos los archivos de log")
        accion_borrar_logs.triggered.connect(self.borrar_logs)
        menu_herramientas.addAction(accion_borrar_logs)

        menu_herramientas.addSeparator()

        # Acción: Abrir carpeta de datos
        accion_data = QAction("Abrir carpeta de &Datos procesados", self)
        accion_data.setStatusTip("Abrir la carpeta con archivos procesados")
        accion_data.triggered.connect(self.abrir_carpeta_data)
        menu_herramientas.addAction(accion_data)

        # --- Menú Vista ---
        menu_vista = menubar.addMenu("&Vista")

        # Acción: Cambiar a tab SEABOARD
        accion_tab_seaboard = QAction("&SEABOARD", self)
        accion_tab_seaboard.setShortcut("Ctrl+1")
        accion_tab_seaboard.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        menu_vista.addAction(accion_tab_seaboard)

        # Acción: Cambiar a tab CASA DEL AGRICULTOR
        accion_tab_casa = QAction("&CASA DEL AGRICULTOR", self)
        accion_tab_casa.setShortcut("Ctrl+2")
        accion_tab_casa.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        menu_vista.addAction(accion_tab_casa)

        # Acción: Cambiar a tab LACTALIS COMPRAS
        accion_tab_lactalis_compras = QAction("LACTALIS &COMPRAS", self)
        accion_tab_lactalis_compras.setShortcut("Ctrl+3")
        accion_tab_lactalis_compras.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        menu_vista.addAction(accion_tab_lactalis_compras)

        # Acción: Cambiar a tab LACTALIS VENTAS
        accion_tab_lactalis_ventas = QAction("LACTALIS &VENTAS", self)
        accion_tab_lactalis_ventas.setShortcut("Ctrl+4")
        accion_tab_lactalis_ventas.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        menu_vista.addAction(accion_tab_lactalis_ventas)

        # --- Menú Ayuda ---
        menu_ayuda = menubar.addMenu("A&yuda")

        # Acción: Acerca de
        accion_acerca = QAction("&Acerca de", self)
        accion_acerca.setStatusTip("Información sobre la aplicación")
        accion_acerca.triggered.connect(self.mostrar_acerca_de)
        menu_ayuda.addAction(accion_acerca)

        # Acción: Documentación
        accion_docs = QAction("&Documentación", self)
        accion_docs.setStatusTip("Ver documentación de uso")
        accion_docs.triggered.connect(self.mostrar_documentacion)
        menu_ayuda.addAction(accion_docs)

    def crear_status_bar(self):
        """Crea la barra de estado en la parte inferior"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Mensaje por defecto
        status_bar.showMessage(f"Listo - {get_version_string()}")

        # Información adicional permanente
        info_label = QLabel("Sistema REGGIS")
        info_label.setStyleSheet("color: #7f8c8d; padding-right: 10px;")
        status_bar.addPermanentWidget(info_label)

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        window_geo = self.frameGeometry()
        center_point = screen.center()
        window_geo.moveCenter(center_point)
        self.move(window_geo.topLeft())

    # --- Slots de acciones del menú ---

    def verificar_actualizaciones(self):
        """Verifica actualizaciones manualmente"""
        self.statusBar().showMessage("Verificando actualizaciones...")
        self.updater.check_for_updates(show_message_if_no_update=True)
        self.statusBar().showMessage("Listo")

    def abrir_carpeta_logs(self):
        """Abre la carpeta donde se guardan los logs"""
        import os
        import platform
        from config.constants import get_logs_dir

        # Obtener la carpeta de logs según el sistema operativo
        carpeta_logs = get_logs_dir()

        try:
            if platform.system() == 'Windows':
                os.startfile(carpeta_logs)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{carpeta_logs}"')
            else:  # Linux
                os.system(f'xdg-open "{carpeta_logs}"')
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo abrir la carpeta de logs:\n{str(e)}"
            )

    def borrar_logs(self):
        """Elimina todos los archivos de log de la carpeta logs"""
        from config.constants import get_logs_dir

        carpeta_logs = get_logs_dir()
        if not carpeta_logs.exists():
            QMessageBox.information(
                self,
                "Sin archivos",
                "No hay archivos de log para borrar."
            )
            return

        # Contar archivos .log
        archivos_log = list(carpeta_logs.glob('*.log'))
        if not archivos_log:
            QMessageBox.information(
                self,
                "Sin archivos",
                "No hay archivos de log para borrar."
            )
            return

        # Confirmar con el usuario
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de borrar {len(archivos_log)} archivo(s) de log?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                eliminados = 0
                for archivo in archivos_log:
                    archivo.unlink()
                    eliminados += 1

                QMessageBox.information(
                    self,
                    "Logs eliminados",
                    f"Se eliminaron {eliminados} archivo(s) de log exitosamente."
                )
                self.statusBar().showMessage(f"Se eliminaron {eliminados} archivo(s) de log", 3000)

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al eliminar archivos de log:\n{str(e)}"
                )

    def abrir_carpeta_data(self):
        """Abre la carpeta donde se guardan los archivos procesados"""
        import os
        import platform
        from config.constants import get_data_dir

        # Obtener la carpeta de datos según el sistema operativo
        carpeta_data = get_data_dir()

        try:
            if platform.system() == 'Windows':
                os.startfile(carpeta_data)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{carpeta_data}"')
            else:  # Linux
                os.system(f'xdg-open "{carpeta_data}"')
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo abrir la carpeta de datos:\n{str(e)}"
            )

    def mostrar_acerca_de(self):
        """Muestra el diálogo Acerca de"""
        mensaje = f"""
<h2>{APP_NAME}</h2>
<p><b>Versión:</b> {__version__}</p>

<p><b>Descripción:</b><br>
Sistema unificado para procesar facturas electrónicas XML a formato Excel REGGIS
para múltiples clientes.</p>

<p><b>Clientes soportados:</b></p>
<ul>
    <li>SEABOARD - Procesamiento desde SharePoint/Local</li>
    <li>CASA DEL AGRICULTOR - Procesamiento desde archivos ZIP</li>
    <li>LACTALIS COMPRAS - Procesamiento de facturas de compra</li>
    <li>LACTALIS VENTAS - Procesamiento de facturas de venta (Lactalis/Proleche)</li>
</ul>

<p><b>Tecnologías:</b></p>
<ul>
    <li>Python 3.x</li>
    <li>PyQt6 - Interfaz gráfica</li>
    <li>openpyxl - Manipulación de Excel</li>
</ul>

<p><b>Desarrollado por:</b> Sistema REGGIS - CORREAGRO S.A.</p>
        """.strip()

        QMessageBox.about(self, "Acerca de", mensaje)

    def mostrar_documentacion(self):
        """Muestra información de documentación"""
        mensaje = """
<h3>Documentación de Uso</h3>

<p><b>Flujo de trabajo general:</b></p>
<ol>
    <li>Seleccione el tab del cliente que desea procesar</li>
    <li>Configure las opciones según el cliente</li>
    <li>Seleccione la carpeta con los archivos (XML o ZIP)</li>
    <li>Confirme el procesamiento</li>
    <li>Espere a que finalice el procesamiento</li>
    <li>Abra la carpeta de resultados automáticamente</li>
</ol>

<p><b>Atajos de teclado:</b></p>
<ul>
    <li><b>Ctrl+1:</b> Cambiar a tab SEABOARD</li>
    <li><b>Ctrl+2:</b> Cambiar a tab CASA DEL AGRICULTOR</li>
    <li><b>Ctrl+3:</b> Cambiar a tab LACTALIS COMPRAS</li>
    <li><b>Ctrl+4:</b> Cambiar a tab LACTALIS VENTAS</li>
    <li><b>Ctrl+Q:</b> Salir de la aplicación</li>
</ul>

<p><b>LACTALIS VENTAS:</b></p>
<ul>
    <li>Procesa facturas de <b>Lactalis</b> (NIT 800245795) y <b>Proleche</b> (NIT 890903711)</li>
    <li>Detecta automáticamente el vendedor del XML</li>
    <li>Soporta grandes volúmenes (20,000+ archivos)</li>
    <li>Validaciones estrictas de reglas de negocio</li>
</ul>

<p><b>Más información:</b><br>
Consulte el archivo README.md en el directorio de instalación para más detalles.</p>
        """.strip()

        QMessageBox.information(self, "Documentación", mensaje)

    def closeEvent(self, event):
        """
        Maneja el evento de cierre de la ventana

        Args:
            event: QCloseEvent
        """
        # Confirmar cierre
        respuesta = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro que desea cerrar la aplicación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            logger.info("Aplicación cerrada por el usuario")
            event.accept()
        else:
            event.ignore()