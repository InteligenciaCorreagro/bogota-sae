"""
Ventana inicial para seleccionar el cliente
"""

from tkinter import Tk, ttk
import tkinter as tk
from typing import Optional


class SelectorCliente:
    """Ventana inicial para seleccionar el cliente"""

    def __init__(self):
        self.cliente_seleccionado = None
        self.root = Tk()
        self.root.title("Procesador de Facturas - Selector de Cliente")
        self.root.resizable(True, True)
        self.setup_ui()
        self.centrar_ventana()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = min(req_w, screen_w - 120)
        height = min(req_h, screen_h - 120)
        self.root.minsize(width, height)
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Configura la interfaz de selección"""
        main_frame = ttk.Frame(self.root, padding=(20, 18))
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        main_frame.columnconfigure(0, weight=1)

        titulo = ttk.Label(
            main_frame,
            text="PROCESADOR DE FACTURAS ELECTRÓNICAS",
            font=("Arial", 16, "bold"),
            anchor="center",
            wraplength=520
        )
        titulo.grid(row=0, column=0, pady=(6, 8), sticky="ew")

        subtitulo = ttk.Label(
            main_frame,
            text="Seleccione el cliente que desea procesar:",
            font=("Arial", 11),
            anchor="center",
            wraplength=520
        )
        subtitulo.grid(row=1, column=0, pady=(0, 12), sticky="ew")

        ttk.Separator(main_frame, orient='horizontal').grid(
            row=2, column=0, sticky='ew', pady=(0, 12)
        )

        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=3, column=0, pady=(0, 12), sticky="ew")
        botones_frame.columnconfigure(0, weight=1)
        botones_frame.columnconfigure(1, weight=1)

        btn_seaboard = tk.Button(
            botones_frame,
            text="🌐 SEABOARD\n(Procesamiento desde SharePoint/Local)",
            command=lambda: self.seleccionar_cliente("SEABOARD"),
            font=("Arial", 12, "bold"),
            bg="#0078D4",
            fg="white",
            padx=18,
            pady=14,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
        )
        btn_seaboard.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="nsew")

        btn_casa = tk.Button(
            botones_frame,
            text="🌾 CASA DEL AGRICULTOR\n(Procesamiento desde archivos ZIP)",
            command=lambda: self.seleccionar_cliente("CASA_DEL_AGRICULTOR"),
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=18,
            pady=14,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
        )
        btn_casa.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="nsew")

        info_label = ttk.Label(
            main_frame,
            text="💡 Cada cliente tiene su propio flujo de procesamiento optimizado",
            justify=tk.CENTER,
            foreground="gray",
            font=("Arial", 9),
            wraplength=520
        )
        info_label.grid(row=4, column=0, pady=(6, 8), sticky="ew")

        btn_cancel = ttk.Button(main_frame, text="Cerrar", command=self.root.destroy)
        btn_cancel.grid(row=5, column=0, pady=(6, 2), sticky="e")

    def seleccionar_cliente(self, cliente: str):
        """Guarda la selección y cierra la ventana"""
        self.cliente_seleccionado = cliente
        self.root.destroy()

    def ejecutar(self) -> Optional[str]:
        """Muestra el selector y retorna el cliente seleccionado"""
        self.root.mainloop()
        return self.cliente_seleccionado
