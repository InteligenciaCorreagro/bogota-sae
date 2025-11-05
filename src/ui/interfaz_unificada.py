"""
Interfaz que gestiona ambos clientes con botón Volver
"""

import os
import platform
import logging
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from tkinter import Tk, filedialog, messagebox, ttk
import tkinter as tk
from pathlib import Path

from config.constants import REGGIS_HEADERS
from utils.sharepoint_detector import DetectorSharePoint
from processors.seaboard_processor import ProcesadorSeaboard
from processors.casa_del_agricultor_processor import ProcesadorCasaDelAgricultor

logger = logging.getLogger(__name__)


class InterfazUnificada:
    """Interfaz que gestiona ambos clientes con botón Volver"""

    def __init__(self, cliente: str):
        self.cliente = cliente
        self.root = Tk()
        self.root.title(f"Procesador de Facturas - {cliente}")
        self.root.resizable(True, True)

        self.carpeta_entrada = None
        self.carpetas_sharepoint = []
        self.request_return = False

        if cliente == "SEABOARD":
            self.detectar_sharepoint()

        self.setup_ui()
        self.centrar_ventana_por_cliente()

    def centrar_ventana_por_cliente(self):
        """Centra la ventana usando el tamaño requerido por los widgets"""
        self.root.update_idletasks()
        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        cliente_min_map = {
            "SEABOARD": (820, 620),
            "CASA_DEL_AGRICULTOR": (760, 560)
        }
        default_min = (720, 520)
        min_w, min_h = cliente_min_map.get(self.cliente, default_min)

        width = max(req_w, min_w)
        height = max(req_h, min_h)

        width = min(width, screen_w - 120)
        height = min(height, screen_h - 120)

        self.root.minsize(width, height)
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def detectar_sharepoint(self):
        """Detecta carpetas de SharePoint sincronizadas"""
        try:
            self.carpetas_sharepoint = DetectorSharePoint.encontrar_carpetas_sharepoint()
            if self.carpetas_sharepoint:
                logger.info(f"Se encontraron {len(self.carpetas_sharepoint)} carpetas de SharePoint")
        except Exception as e:
            logger.error(f"Error detectando SharePoint: {str(e)}")
            self.carpetas_sharepoint = []

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_frame = ttk.Frame(self.root, padding=(18, 14))
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Barra superior con botón Volver
        top_bar = ttk.Frame(main_frame)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        top_bar.columnconfigure(0, weight=0)
        top_bar.columnconfigure(1, weight=1)

        btn_volver = ttk.Button(top_bar, text="← Volver", command=self.volver_al_selector)
        btn_volver.grid(row=0, column=0, sticky="w")

        titulo = ttk.Label(
            main_frame,
            text=f"PROCESADOR - {self.cliente}",
            font=("Arial", 18, "bold"),
            anchor="center",
            wraplength=680
        )
        titulo.grid(row=1, column=0, columnspan=2, pady=(4, 10), sticky="ew")

        ttk.Separator(main_frame, orient='horizontal').grid(
            row=2, column=0, columnspan=2, sticky='ew', pady=(0, 12)
        )

        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=3, column=0, columnspan=2, pady=(0, 12), sticky="ew")
        botones_frame.columnconfigure(0, weight=1)

        if self.cliente == "SEABOARD":
            self.setup_botones_seaboard(botones_frame)
        else:
            self.setup_botones_casa(botones_frame)

        # Barra de progreso
        self.progress = ttk.Progressbar(
            main_frame,
            orient='horizontal',
            mode='indeterminate'
        )
        self.progress.grid(row=4, column=0, columnspan=2, pady=(8, 8), sticky="ew")

        # Label de estado
        self.estado_label = ttk.Label(
            main_frame,
            text="",
            font=("Arial", 10),
            wraplength=680,
            anchor="w",
            justify="left"
        )
        self.estado_label.grid(row=5, column=0, columnspan=2, pady=(2, 6), sticky="ew")

        # Espacio inferior
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(6, 4))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=0)

        self.lbl_resultados = ttk.Label(bottom_frame, text="", font=("Arial", 9), foreground="gray")
        self.lbl_resultados.grid(row=0, column=0, sticky="w")

        btn_cerrar = ttk.Button(bottom_frame, text="Cerrar", command=self.root.destroy)
        btn_cerrar.grid(row=0, column=1, sticky="e", padx=(6, 0))

    def setup_botones_seaboard(self, parent):
        """Configura los botones específicos para SEABOARD"""
        if self.carpetas_sharepoint:
            info_sp = ttk.Label(
                parent,
                text=f"Se detectaron {len(self.carpetas_sharepoint)} carpeta(s) de SharePoint sincronizada(s)",
                font=("Arial", 10),
                foreground="green",
                wraplength=640
            )
            info_sp.pack(fill="x", pady=(0, 6))

            btn_sharepoint = tk.Button(
                parent,
                text="BUSCAR EN SHAREPOINT SINCRONIZADO",
                command=self.seleccionar_desde_sharepoint,
                font=("Arial", 12, "bold"),
                bg="#0078D4",
                fg="white",
                padx=12,
                pady=12,
                cursor="hand2",
                relief=tk.RAISED,
                bd=3
            )
            btn_sharepoint.pack(fill="x", pady=(0, 8))

        btn_local = tk.Button(
            parent,
            text="BUSCAR EN CARPETA LOCAL",
            command=self.seleccionar_y_procesar_seaboard,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=12,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        )
        btn_local.pack(fill="x", pady=(0, 2))

    def setup_botones_casa(self, parent):
        """Configura los botones específicos para CASA DEL AGRICULTOR"""
        info = ttk.Label(
            parent,
            text="Seleccione la carpeta que contiene los archivos ZIP de facturas",
            font=("Arial", 10),
            wraplength=640
        )
        info.pack(fill="x", pady=(0, 6))

        btn_procesar = tk.Button(
            parent,
            text="SELECCIONAR CARPETA CON ARCHIVOS ZIP",
            command=self.seleccionar_y_procesar_casa,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=12,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        )
        btn_procesar.pack(fill="x", pady=(0, 2))

    def volver_al_selector(self):
        """Marca la intención de volver y cierra la ventana actual"""
        self.request_return = True
        self.root.destroy()

    def seleccionar_desde_sharepoint(self):
        """Muestra un diálogo para seleccionar una carpeta de SharePoint"""
        if not self.carpetas_sharepoint:
            messagebox.showinfo("No hay carpetas", "No se detectaron carpetas de SharePoint")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Seleccionar Carpeta de SharePoint")
        ventana.geometry("700x500")
        ventana.transient(self.root)
        ventana.grab_set()

        frame = ttk.Frame(ventana, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Carpetas de SharePoint Detectadas", font=("Arial", 14, "bold")).pack(pady=10)

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame, font=("Arial", 10), yscrollcommand=scrollbar.set, height=15)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        for carpeta in self.carpetas_sharepoint:
            listbox.insert(tk.END, str(carpeta))

        def seleccionar():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Selección requerida", "Seleccione una carpeta")
                return

            carpeta_sel = self.carpetas_sharepoint[sel[0]]
            ventana.destroy()
            self.procesar_carpeta_xml(carpeta_sel)

        ttk.Button(frame, text="Procesar Carpeta Seleccionada", command=seleccionar).pack(pady=10)

    def seleccionar_y_procesar_seaboard(self):
        """Permite seleccionar una carpeta local con archivos XML"""
        carpeta = filedialog.askdirectory(title="Seleccione la carpeta con archivos XML")

        if not carpeta:
            return

        self.procesar_carpeta_xml(Path(carpeta))

    def procesar_carpeta_xml(self, carpeta: Path):
        """Procesa la carpeta con archivos XML"""
        archivos_xml = list(carpeta.glob("*.xml"))

        if not archivos_xml:
            messagebox.showerror("Sin archivos", "No se encontraron archivos XML")
            return

        respuesta = messagebox.askyesno(
            "Confirmar",
            f"Se encontraron {len(archivos_xml)} archivo(s) XML.\n\n¿Procesar ahora?"
        )

        if not respuesta:
            return

        self.carpeta_entrada = carpeta
        self.progress.start()
        self.estado_label.config(text=f"Procesando {len(archivos_xml)} archivo(s)...", foreground="orange")
        self.root.update()
        self.root.after(100, self.ejecutar_procesamiento_seaboard)

    def seleccionar_y_procesar_casa(self):
        """Permite seleccionar una carpeta con archivos ZIP"""
        carpeta = filedialog.askdirectory(title="Seleccione la carpeta con archivos ZIP")

        if not carpeta:
            return

        self.carpeta_entrada = Path(carpeta)

        zip_files = list(self.carpeta_entrada.glob("*.zip"))

        if not zip_files:
            messagebox.showerror("Sin archivos", "No se encontraron archivos ZIP")
            return

        respuesta = messagebox.askyesno(
            "Confirmar",
            f"Se encontraron {len(zip_files)} archivo(s) ZIP.\n\n¿Procesar ahora?"
        )

        if not respuesta:
            return

        self.progress.start()
        self.estado_label.config(text=f"Procesando {len(zip_files)} archivo(s)...", foreground="orange")
        self.root.update()
        self.root.after(100, self.ejecutar_procesamiento_casa)

    def buscar_o_crear_plantilla(self) -> Path:
        """Busca o crea la plantilla REGGIS"""
        script_dir = Path(__file__).parent.parent.parent

        plantilla = script_dir / "Plantilla_REGGIS.xlsx"

        if not plantilla.exists():
            self.crear_plantilla_base(plantilla)

        return plantilla

    def crear_plantilla_base(self, ruta: Path):
        """Crea una plantilla base de Excel"""
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

    def ejecutar_procesamiento_seaboard(self):
        """Ejecuta el procesamiento para SEABOARD"""
        try:
            plantilla = self.buscar_o_crear_plantilla()
            procesador = ProcesadorSeaboard(self.carpeta_entrada, plantilla)
            carpeta_salida = procesador.procesar()

            self.progress.stop()
            self.estado_label.config(text="Proceso completado exitosamente", foreground="green")

            respuesta = messagebox.askyesno(
                "Éxito",
                f"Proceso completado!\n\nArchivos guardados en:\n{carpeta_salida.name}\n\n¿Abrir carpeta?"
            )

            if respuesta:
                self.abrir_carpeta(carpeta_salida)

        except Exception as e:
            self.progress.stop()
            self.estado_label.config(text="Error en el procesamiento", foreground="red")
            messagebox.showerror("Error", f"Error: {str(e)}")

    def ejecutar_procesamiento_casa(self):
        """Ejecuta el procesamiento para CASA DEL AGRICULTOR"""
        try:
            carpeta_salida = self.carpeta_entrada.parent / "Resultados_CASA_DEL_AGRICULTOR"
            carpeta_salida.mkdir(exist_ok=True)

            procesador = ProcesadorCasaDelAgricultor(self.carpeta_entrada, carpeta_salida)
            procesador.procesar()

            self.progress.stop()
            self.estado_label.config(text="Proceso completado exitosamente", foreground="green")

            respuesta = messagebox.askyesno(
                "Éxito",
                f"Proceso completado!\n\nArchivos guardados en:\n{carpeta_salida.name}\n\n¿Abrir carpeta?"
            )

            if respuesta:
                self.abrir_carpeta(carpeta_salida)

        except Exception as e:
            self.progress.stop()
            self.estado_label.config(text="Error en el procesamiento", foreground="red")
            messagebox.showerror("Error", f"Error: {str(e)}")

    def abrir_carpeta(self, carpeta: Path):
        """Abre la carpeta en el explorador de archivos del sistema"""
        if platform.system() == 'Windows':
            os.startfile(carpeta)
        elif platform.system() == 'Darwin':
            os.system(f'open "{carpeta}"')
        else:
            os.system(f'xdg-open "{carpeta}"')

    def ejecutar(self):
        """Inicia el loop principal de la interfaz"""
        self.root.mainloop()
