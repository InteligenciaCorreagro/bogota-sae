"""
Tab para procesamiento de facturas LACTALIS VENTAS
Optimizado para grandes volúmenes (20,000+ XML) con progreso detallado
"""

import os
import platform
import logging
import openpyxl
from pathlib import Path
from openpyxl.styles import Font, PatternFill, Alignment

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QProgressBar, QFileDialog,
                              QMessageBox, QGroupBox, QTextEdit, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from src.config.constants import REGGIS_HEADERS
from processors.lactalis_ventas_processor import ProcesadorLactalisVentas
from src.database.lactalis_database import LactalisDatabase
from src.database.excel_importer import ExcelImporter, ExcelImporterError

logger = logging.getLogger(__name__)


class ProcesamientoThread(QThread):
    """Thread para ejecutar procesamiento en segundo plano con reportes de progreso"""
    progress = pyqtSignal(int, int, str)  # processed, total, message
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


class TabLactalisVentas(QWidget):
    """
    Tab para procesamiento de facturas LACTALIS VENTAS
    
    REGLAS DE NEGOCIO IMPLEMENTADAS:
    • Solo procesa FACTURAS (Invoice), NO notas crédito/débito
    • Cantidad debe ser > 0
    • Precio unitario debe ser > 0
    • Total debe ser > 0
    
    OPTIMIZACIONES:
    • Procesamiento por lotes para grandes volúmenes
    • Progreso detallado en tiempo real
    • Estadísticas completas de procesamiento
    • Validaciones tempranas para descartar archivos inválidos
    """

    def __init__(self):
        super().__init__()
        self.carpeta_entrada = None
        self.procesamiento_thread = None
        self.db = LactalisDatabase()
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del tab"""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Título ---
        titulo = QLabel("💼 PROCESADOR LACTALIS VENTAS")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2980b9; padding: 10px;")
        main_layout.addWidget(titulo)

        # --- Descripción ---
        descripcion = QLabel(
            "Procesa archivos ZIP y XML de FACTURAS de ventas de Lactalis.\n"
            "⚠️ Solo facturas (Invoice) - NO se procesan notas crédito/débito"
        )
        descripcion.setFont(QFont("Arial", 9))
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        descripcion.setStyleSheet("color: #555; padding: 5px;")
        descripcion.setWordWrap(True)
        main_layout.addWidget(descripcion)

        # --- Group Box: Gestión de Base de Datos ---
        group_db = QGroupBox("🗄️ Gestión de Base de Datos")
        group_db.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        db_layout = QVBoxLayout()
        db_layout.setSpacing(10)

        # Info de BD
        db_info = QLabel(
            f"Base de datos: {self.db.db_path}\n"
            f"Materiales: {self.db.contar_materiales()} | Clientes: {self.db.contar_clientes()}"
        )
        db_info.setFont(QFont("Arial", 9))
        db_info.setStyleSheet("color: #34495e; padding: 5px;")
        db_info.setWordWrap(True)
        db_layout.addWidget(db_info)
        self.db_info_label = db_info

        # Botones de importación horizontal
        btn_layout = QHBoxLayout()

        # Botón importar materiales
        btn_importar_materiales = QPushButton("📦 Importar Materiales")
        btn_importar_materiales.setMinimumHeight(40)
        btn_importar_materiales.setFont(QFont("Arial", 10))
        btn_importar_materiales.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        btn_importar_materiales.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_importar_materiales.clicked.connect(self.importar_materiales)
        btn_layout.addWidget(btn_importar_materiales)

        # Botón importar clientes
        btn_importar_clientes = QPushButton("👥 Importar Clientes")
        btn_importar_clientes.setMinimumHeight(40)
        btn_importar_clientes.setFont(QFont("Arial", 10))
        btn_importar_clientes.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #21618c;
            }
        """)
        btn_importar_clientes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_importar_clientes.clicked.connect(self.importar_clientes)
        btn_layout.addWidget(btn_importar_clientes)

        db_layout.addLayout(btn_layout)

        # Nota sobre formato
        formato_note = QLabel(
            "💡 Materiales: CODIGO, DESCRIPCION, SOCIEDAD (usar: 'Parmalat' o 'Proleche')\n"
            "💡 Clientes: Cód.Padre, Nombre Código Padre, NIT (si dice 'no nit' no se registra)"
        )
        formato_note.setFont(QFont("Arial", 8))
        formato_note.setStyleSheet("color: #7f8c8d; padding: 5px;")
        formato_note.setWordWrap(True)
        db_layout.addWidget(formato_note)

        # Checkboxes para validaciones
        validaciones_layout = QHBoxLayout()

        self.checkbox_validar_materiales = QCheckBox("✓ Validar materiales contra BD")
        self.checkbox_validar_materiales.setFont(QFont("Arial", 9))
        self.checkbox_validar_materiales.setStyleSheet("color: #2c3e50;")
        validaciones_layout.addWidget(self.checkbox_validar_materiales)

        self.checkbox_validar_clientes = QCheckBox("✓ Validar clientes contra BD")
        self.checkbox_validar_clientes.setFont(QFont("Arial", 9))
        self.checkbox_validar_clientes.setStyleSheet("color: #2c3e50;")
        validaciones_layout.addWidget(self.checkbox_validar_clientes)

        db_layout.addLayout(validaciones_layout)

        group_db.setLayout(db_layout)
        main_layout.addWidget(group_db)

        # --- Group Box: Reglas de Negocio ---
        group_reglas = QGroupBox("📋 Reglas de Validación")
        group_reglas.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        reglas_layout = QVBoxLayout()
        reglas_layout.setSpacing(5)

        reglas_text = QLabel(
            "✓ Solo FACTURAS (Invoice) - se rechazan notas crédito/débito\n"
            "✓ Cantidad > 0 (se rechazan líneas con cantidad en 0 o negativa)\n"
            "✓ Precio unitario > 0 (se rechazan líneas con precio en 0 o negativo)\n"
            "✓ Total > 0 (se rechazan líneas con total en 0 o negativo)"
        )
        reglas_text.setFont(QFont("Arial", 9))
        reglas_text.setStyleSheet("color: #27ae60; padding: 5px;")
        reglas_text.setWordWrap(True)
        reglas_layout.addWidget(reglas_text)

        group_reglas.setLayout(reglas_layout)
        main_layout.addWidget(group_reglas)

        # --- Group Box: Selección de Archivos ---
        group_archivos = QGroupBox("📁 Seleccionar Archivos")
        group_archivos.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        archivos_layout = QVBoxLayout()
        archivos_layout.setSpacing(10)

        info_label = QLabel(
            "ℹ️ Seleccione la carpeta con archivos ZIP y/o XML de facturas.\n"
            "Optimizado para procesar 20,000+ archivos"
        )
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet("color: #34495e; padding: 5px;")
        info_label.setWordWrap(True)
        archivos_layout.addWidget(info_label)

        # Botón seleccionar carpeta
        btn_seleccionar = QPushButton("📂 SELECCIONAR CARPETA CON ARCHIVOS")
        btn_seleccionar.setMinimumHeight(60)
        btn_seleccionar.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn_seleccionar.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #21618c;
            }
            QPushButton:pressed {
                background-color: #1b4f72;
            }
        """)
        btn_seleccionar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_seleccionar.clicked.connect(self.seleccionar_carpeta)
        archivos_layout.addWidget(btn_seleccionar)

        group_archivos.setLayout(archivos_layout)
        main_layout.addWidget(group_archivos)

        # --- Barra de Progreso ---
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2980b9;
            }
        """)
        main_layout.addWidget(self.progress)

        # --- Label de Estado ---
        self.estado_label = QLabel("")
        self.estado_label.setFont(QFont("Arial", 10))
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.estado_label.setStyleSheet("padding: 10px;")
        main_layout.addWidget(self.estado_label)

        # --- Consola de Log ---
        group_log = QGroupBox("📊 Progreso Detallado")
        group_log.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        log_layout = QVBoxLayout()
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(150)
        self.log_console.setFont(QFont("Courier", 9))
        self.log_console.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
        """)
        log_layout.addWidget(self.log_console)
        
        group_log.setLayout(log_layout)
        main_layout.addWidget(group_log)

        # Espaciador
        main_layout.addStretch()

        # --- Información adicional ---
        info_footer = QLabel(
            "💡 Optimizado para grandes volúmenes. Procesamiento por lotes.\n"
            "Las facturas inválidas se rechazan automáticamente según las reglas."
        )
        info_footer.setFont(QFont("Arial", 8))
        info_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_footer.setStyleSheet("color: #7f8c8d; padding: 10px;")
        info_footer.setWordWrap(True)
        main_layout.addWidget(info_footer)

        self.setLayout(main_layout)

    def agregar_log(self, mensaje: str):
        """Agrega un mensaje a la consola de log"""
        self.log_console.append(mensaje)
        # Auto-scroll al final
        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def seleccionar_carpeta(self):
        """Permite seleccionar una carpeta con archivos ZIP/XML"""
        carpeta = QFileDialog.getExistingDirectory(
            self,
            "Seleccione la carpeta con archivos ZIP y/o XML de Lactalis Ventas",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if not carpeta:
            return

        self.carpeta_entrada = Path(carpeta)

        # Buscar archivos ZIP y XML
        zip_files = list(self.carpeta_entrada.glob("*.zip"))
        xml_files = list(self.carpeta_entrada.glob("*.xml"))
        total_archivos = len(zip_files) + len(xml_files)

        if total_archivos == 0:
            QMessageBox.critical(
                self,
                "Sin archivos",
                "No se encontraron archivos ZIP ni XML en la carpeta seleccionada"
            )
            return

        # Confirmar procesamiento
        respuesta = QMessageBox.question(
            self,
            "Confirmar procesamiento",
            f"Se encontraron:\n"
            f"  • {len(zip_files)} archivo(s) ZIP\n"
            f"  • {len(xml_files)} archivo(s) XML\n"
            f"  • {total_archivos} archivos TOTALES\n\n"
            f"Carpeta: {self.carpeta_entrada.name}\n\n"
            f"REGLAS DE VALIDACIÓN:\n"
            f"  ✓ Solo FACTURAS (Invoice)\n"
            f"  ✓ Cantidad > 0\n"
            f"  ✓ Precio unitario > 0\n"
            f"  ✓ Total > 0\n\n"
            f"¿Procesar ahora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.iniciar_procesamiento()

    def buscar_o_crear_plantilla(self) -> Path:
        """Busca o crea la plantilla REGGIS Excel"""
        script_dir = Path(__file__).parent.parent.parent.parent
        plantilla = script_dir / "Plantilla_REGGIS.xlsx"

        if not plantilla.exists():
            logger.info(f"Plantilla no encontrada. Creando en: {plantilla}")
            self.crear_plantilla_base(plantilla)

        return plantilla

    def crear_plantilla_base(self, ruta: Path):
        """Crea una plantilla base de Excel con formato REGGIS"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Datos"

        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")

        for col, header in enumerate(REGGIS_HEADERS, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        wb.save(ruta)
        logger.info(f"Plantilla creada exitosamente: {ruta}")

    def actualizar_progreso(self, processed: int, total: int, message: str):
        """Callback para actualizar el progreso"""
        if total > 0:
            porcentaje = int((processed / total) * 100)
            self.progress.setValue(porcentaje)
            
        self.agregar_log(f"[{processed}/{total}] {message}")

    def iniciar_procesamiento(self):
        """Inicia el procesamiento en segundo plano"""
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log_console.clear()
        
        self.estado_label.setText("⏳ Procesando archivos de LACTALIS VENTAS...")
        self.estado_label.setStyleSheet("color: #f39c12; padding: 10px; font-weight: bold;")
        
        self.agregar_log("=" * 60)
        self.agregar_log("Iniciando procesamiento de LACTALIS VENTAS...")
        self.agregar_log("=" * 60)

        # Obtener plantilla
        plantilla = self.buscar_o_crear_plantilla()

        # Obtener estado de checkboxes
        validar_materiales = self.checkbox_validar_materiales.isChecked()
        validar_clientes = self.checkbox_validar_clientes.isChecked()

        # Crear procesador con callback de progreso y validaciones
        procesador = ProcesadorLactalisVentas(
            self.carpeta_entrada,
            plantilla,
            progress_callback=self.actualizar_progreso,
            database=self.db,
            validar_materiales=validar_materiales,
            validar_clientes=validar_clientes
        )

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
            
            self.agregar_log("=" * 60)
            self.agregar_log("✅ PROCESO COMPLETADO EXITOSAMENTE")
            self.agregar_log("=" * 60)

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
            
            self.agregar_log("=" * 60)
            self.agregar_log("❌ ERROR EN EL PROCESAMIENTO")
            self.agregar_log(f"Error: {message}")
            self.agregar_log("=" * 60)
            
            QMessageBox.critical(
                self,
                "Error de procesamiento",
                f"Ocurrió un error durante el procesamiento:\n\n{message}"
            )

    def importar_materiales(self):
        """Importa materiales desde un archivo Excel"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel de Materiales",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not archivo:
            return

        try:
            # Validar formato del archivo
            es_valido, mensaje = ExcelImporter.validar_archivo_materiales(archivo)
            if not es_valido:
                QMessageBox.critical(
                    self,
                    "Formato inválido",
                    f"El archivo no tiene el formato correcto:\n\n{mensaje}\n\n"
                    f"Se esperan los encabezados: CODIGO, DESCRIPCION, SOCIEDAD"
                )
                return

            # Importar materiales
            materiales = ExcelImporter.importar_materiales_desde_excel(archivo)

            if not materiales:
                QMessageBox.warning(
                    self,
                    "Sin datos",
                    "No se encontraron materiales para importar"
                )
                return

            # Guardar en base de datos
            nuevos, existentes, errores = self.db.importar_materiales(materiales)

            # Actualizar label de info
            self.db_info_label.setText(
                f"Base de datos: {self.db.db_path}\n"
                f"Materiales: {self.db.contar_materiales()} | Clientes: {self.db.contar_clientes()}"
            )

            # Mostrar resultado
            QMessageBox.information(
                self,
                "Importación completada",
                f"Materiales importados:\n\n"
                f"✓ Nuevos: {nuevos}\n"
                f"⊙ Ya existentes: {existentes}\n"
                f"✗ Errores: {errores}\n\n"
                f"Total en BD: {self.db.contar_materiales()}"
            )

        except ExcelImporterError as e:
            QMessageBox.critical(
                self,
                "Error de importación",
                f"Error importando materiales:\n\n{str(e)}"
            )
        except Exception as e:
            logger.error(f"Error importando materiales: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error inesperado:\n\n{str(e)}"
            )

    def importar_clientes(self):
        """Importa clientes desde un archivo Excel"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel de Clientes",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not archivo:
            return

        try:
            # Validar formato del archivo
            es_valido, mensaje = ExcelImporter.validar_archivo_clientes(archivo)
            if not es_valido:
                QMessageBox.critical(
                    self,
                    "Formato inválido",
                    f"El archivo no tiene el formato correcto:\n\n{mensaje}\n\n"
                    f"Se esperan los encabezados: Cód.Padre, Nombre Código Padre, NIT"
                )
                return

            # Importar clientes
            clientes = ExcelImporter.importar_clientes_desde_excel(archivo)

            if not clientes:
                QMessageBox.warning(
                    self,
                    "Sin datos",
                    "No se encontraron clientes para importar"
                )
                return

            # Guardar en base de datos
            nuevos, existentes, errores = self.db.importar_clientes(clientes)

            # Actualizar label de info
            self.db_info_label.setText(
                f"Base de datos: {self.db.db_path}\n"
                f"Materiales: {self.db.contar_materiales()} | Clientes: {self.db.contar_clientes()}"
            )

            # Mostrar resultado
            QMessageBox.information(
                self,
                "Importación completada",
                f"Clientes importados:\n\n"
                f"✓ Nuevos: {nuevos}\n"
                f"⊙ Ya existentes: {existentes}\n"
                f"✗ Errores/rechazados: {errores}\n\n"
                f"Total en BD: {self.db.contar_clientes()}\n\n"
                f"Nota: Los clientes con 'no nit' no se registran"
            )

        except ExcelImporterError as e:
            QMessageBox.critical(
                self,
                "Error de importación",
                f"Error importando clientes:\n\n{str(e)}"
            )
        except Exception as e:
            logger.error(f"Error importando clientes: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error inesperado:\n\n{str(e)}"
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