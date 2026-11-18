"""Ventana 'Información' (Acerca de)."""
import tkinter as tk

import util.util_imagenes as util_img
import util.util_ui as ui
import util.util_ventana as util_ventana
from conf import (ACENTO, ACENTO_SUAVE, APP_NOMBRE, APP_VERSION, AUTOR_EMAIL,
                  AUTOR_NOMBRE, BORDE, RUTA_IMAGENES, SUPERFICIE, TEXTO,
                  TEXTO_SUAVE)
from util.util_ui import Boton, px


class FormularioInfoDesign(tk.Toplevel):
    def __init__(self, padre=None) -> None:
        super().__init__(padre)
        self.withdraw()
        self.configuracionVentana()
        self.construirWidgets()
        self.update_idletasks()
        ancho, alto = px(400), self.winfo_reqheight()
        if padre is not None:
            self.transient(padre)
            util_ventana.centrarSobre(self, padre, ancho, alto)
        else:
            util_ventana.centrarVentana(self, ancho, alto)
        self.deiconify()
        self.grab_set()
        self.focus_set()

    def configuracionVentana(self):
        self.title('Información')
        self.configure(bg=SUPERFICIE)
        self.resizable(False, False)
        try:
            self.iconbitmap(str(RUTA_IMAGENES / 'ICON.ico'))
        except tk.TclError:
            pass
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self.destroy())

    def construirWidgets(self):
        cuerpo = tk.Frame(self, bg=SUPERFICIE, padx=px(28), pady=px(26))
        cuerpo.pack(fill="both", expand=True)

        self.logo = util_img.imagen_circular('logoPerfil.png', px(64), ACENTO_SUAVE)
        tk.Label(cuerpo, image=self.logo, bg=SUPERFICIE, bd=0).pack()
        ui.etiqueta(cuerpo, APP_NOMBRE, 19, "semibold", TEXTO).pack(pady=(px(14), 0))

        version = ui.Pildora(cuerpo, f"Versión {APP_VERSION}", seleccionada=True,
                             alto=24, tam=12, borde=False)
        version.pack(pady=(px(8), px(18)))

        datos = tk.Frame(cuerpo, bg=SUPERFICIE, highlightthickness=max(1, px(1)),
                         highlightbackground=BORDE)
        datos.pack(fill="x")
        filas = [("Autor", AUTOR_NOMBRE), ("Contacto", AUTOR_EMAIL),
                 ("Tecnología", "Python · Tkinter · Pillow")]
        for i, (clave, valor) in enumerate(filas):
            if i:
                ui.separador(datos)
            fila = tk.Frame(datos, bg=SUPERFICIE, padx=px(14), pady=px(10))
            fila.pack(fill="x")
            ui.etiqueta(fila, clave, 13, color=TEXTO_SUAVE).pack(side="left")
            ui.etiqueta(fila, valor, 13, "semibold", TEXTO).pack(side="right")

        ui.etiqueta(cuerpo, "Atajos: Ctrl+1/2/3 cambiar de sección · Ctrl+N nuevo "
                            "contacto · Ctrl+F buscar", 12, color=TEXTO_SUAVE,
                    wraplength=px(330), justify="center").pack(pady=(px(16), 0))

        Boton(cuerpo, "Cerrar", self.destroy, "secundario", ancho=344).pack(
            pady=(px(18), 0))
