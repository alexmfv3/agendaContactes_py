"""Ventana principal: menú lateral + zona de contenido."""
import tkinter as tk

import util.util_imagenes as util_img
import util.util_ui as ui
import util.util_ventana as util_ventana
from conf import (ACENTO, ACENTO_SUAVE, APP_NOMBRE, AUTOR_EMAIL, AUTOR_NOMBRE,
                  BORDE, FONDO, RUTA_IMAGENES, SUPERFICIE, TEXTO,
                  TEXTO_SECUNDARIO, TEXTO_SUAVE, TEXTO_TENUE)
from formularios.form_aed_design import FormularioAEDDesign
from formularios.form_escritorio_design import FormularioEscritorioDesign
from formularios.form_graficos_design import FormularioGraficosDesign
from formularios.form_info_design import FormularioInfoDesign
from util.util_agenda import cargar_contactos
from util.util_ui import fuente, px

ANCHO_MENU = 248


class ElementoMenu(tk.Canvas):
    """Opción del menú lateral con icono, texto, hover y estado activo."""

    def __init__(self, padre, texto, icono, comando):
        super().__init__(padre, height=px(42), bg=SUPERFICIE, highlightthickness=0,
                         bd=0, cursor="hand2")
        self.texto, self.icono, self.comando = texto, icono, comando
        self.activo = False
        self.contador = None
        self._hover = False
        self.bind("<Configure>", lambda e: self.dibujar())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", lambda e: self.comando())

    def _set_hover(self, valor):
        self._hover = valor
        self.dibujar()

    def marcar(self, activo):
        self.activo = activo
        self.dibujar()

    def poner_contador(self, valor):
        self.contador = valor
        self.dibujar()

    def dibujar(self):
        self.delete("all")
        w, h = self.winfo_width(), px(42)
        if w < 10:
            return
        if self.activo:
            fondo, color, color_ico, peso = ACENTO_SUAVE, ACENTO, ACENTO, "semibold"
        elif self._hover:
            fondo, color, color_ico, peso = "#f2f4f7", TEXTO, TEXTO_SECUNDARIO, "normal"
        else:
            fondo, color, color_ico, peso = None, TEXTO_SECUNDARIO, TEXTO_SUAVE, "normal"
        if fondo:
            self._fondo = util_img.rect_redondeado(w, h, px(9), fondo)
            self.create_image(0, 0, anchor="nw", image=self._fondo)
        self._ico = util_img.icono(self.icono, px(19), color_ico)
        self.create_image(px(14), h // 2, anchor="w", image=self._ico)
        self.create_text(px(46), h // 2, anchor="w", text=self.texto,
                         font=fuente(14, peso), fill=color)
        if self.contador is not None:
            f = fuente(12, "semibold")
            texto = str(self.contador)
            cw = max(px(24), ui.medir(texto, f) + px(14))
            ch = px(20)
            fondo_c = "#ffffff" if self.activo else "#f2f4f7"
            self._cont = util_img.rect_redondeado(cw, ch, ch // 2, fondo_c)
            self.create_image(w - px(12), h // 2, anchor="e", image=self._cont)
            self.create_text(w - px(12) - cw // 2, h // 2, text=texto, font=f,
                             fill=ACENTO if self.activo else TEXTO_SUAVE)


class FormularioMaestroDesign(tk.Tk):

    def __init__(self):
        ui.activar_alta_resolucion()
        super().__init__()
        ui.iniciar(self)
        self.configuracionVentana()
        self.paneles()
        self.controlesBarraLateral()
        self.atajosTeclado()
        self.pagina_actual = None
        self.abrirPanelContactos()

    # ------------------------------------------------------------------
    # Configuración general
    # ------------------------------------------------------------------
    def configuracionVentana(self):
        self.title(APP_NOMBRE)
        try:
            self.iconbitmap(str(RUTA_IMAGENES / 'ICON.ico'))
        except tk.TclError:
            try:
                self._icono = util_img.leerImagen(RUTA_IMAGENES / 'logoPerfil.png', (64, 64))
                self.iconphoto(True, self._icono)
            except Exception:
                pass
        self.configure(bg=FONDO)
        w, h = px(1200), px(760)
        self.minsize(px(1040), px(660))
        util_ventana.centrarVentana(self, w, h)

    def paneles(self):
        # MENÚ LATERAL
        self.menu_lateral = tk.Frame(self, bg=SUPERFICIE, width=px(ANCHO_MENU))
        self.menu_lateral.pack(side=tk.LEFT, fill='y')
        self.menu_lateral.pack_propagate(False)
        # Línea que separa el menú del contenido
        tk.Frame(self, bg=BORDE, width=max(1, px(1))).pack(side=tk.LEFT, fill='y')

        # CUERPO PRINCIPAL
        self.cuerpo_principal = tk.Frame(self, bg=FONDO, padx=px(32), pady=px(28))
        self.cuerpo_principal.pack(side=tk.RIGHT, fill='both', expand=True)

    def controlesBarraLateral(self):
        menu = self.menu_lateral
        interior = tk.Frame(menu, bg=SUPERFICIE, padx=px(16))
        interior.pack(fill="both", expand=True)

        # Logo
        self.logo = util_img.logo_app(px(32))
        tk.Label(interior, image=self.logo, bg=SUPERFICIE, bd=0).pack(
            anchor="w", padx=px(10), pady=(px(26), px(28)))

        ui.etiqueta(interior, "MENÚ", 11.5, "semibold", TEXTO_TENUE).pack(
            anchor="w", padx=px(12), pady=(0, px(8)))

        self.elementos = {}
        opciones = [
            ("escritorio", "Escritorio", "escritorio", self.abrirPanelContactos),
            ("contactos", "Contactos", "contactos", self.abrirAEDContactos),
            ("graficos", "Gráficos", "graficos", self.abrirGraficos),
        ]
        for clave, texto, icono, comando in opciones:
            elemento = ElementoMenu(interior, texto, icono, comando)
            elemento.pack(fill="x", pady=(0, px(4)))
            self.elementos[clave] = elemento

        # Parte inferior: información + perfil
        abajo = tk.Frame(interior, bg=SUPERFICIE)
        abajo.pack(side="bottom", fill="x", pady=(0, px(18)))

        ElementoMenu(abajo, "Información", "info", self.abrirPanelInformacion).pack(
            fill="x", pady=(0, px(12)))
        ui.separador(abajo, pady=(0, px(14)))

        perfil = tk.Frame(abajo, bg=SUPERFICIE)
        perfil.pack(fill="x", padx=px(6))
        self.perfil = util_img.imagen_circular('logoPerfil.png', px(40), "#eef0ff")
        tk.Label(perfil, image=self.perfil, bg=SUPERFICIE, bd=0).pack(side="left")
        datos = tk.Frame(perfil, bg=SUPERFICIE)
        datos.pack(side="left", padx=(px(10), 0))
        ui.etiqueta(datos, AUTOR_NOMBRE, 13.5, "semibold", TEXTO).pack(anchor="w")
        ui.etiqueta(datos, AUTOR_EMAIL, 12, color=TEXTO_SUAVE).pack(anchor="w")

        self.actualizarContador()

    def atajosTeclado(self):
        self.bind_all("<Control-Key-1>", lambda e: self.abrirPanelContactos())
        self.bind_all("<Control-Key-2>", lambda e: self.abrirAEDContactos())
        self.bind_all("<Control-Key-3>", lambda e: self.abrirGraficos())
        self.bind_all("<Control-n>", lambda e: self.abrirAEDContactos(nuevo=True))
        self.bind_all("<Control-f>", lambda e: self._buscar())

    def _buscar(self):
        if self.pagina_actual != "contactos":
            self.abrirAEDContactos()
        if hasattr(self, "_pantalla") and hasattr(self._pantalla, "campoBuscar"):
            self._pantalla.campoBuscar.enfocar()

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------
    def _activar(self, clave):
        self.pagina_actual = clave
        for nombre, elemento in self.elementos.items():
            elemento.marcar(nombre == clave)
        self.limpiarPanel(self.cuerpo_principal)

    def actualizarContador(self):
        self.elementos["contactos"].poner_contador(len(cargar_contactos()))

    def abrirPanelInformacion(self):
        FormularioInfoDesign(self)

    def abrirPanelContactos(self):
        self._activar("escritorio")
        self._pantalla = FormularioEscritorioDesign(self.cuerpo_principal, self)

    def abrirAEDContactos(self, nuevo=False):
        if self.pagina_actual != "contactos":
            self._activar("contactos")
            self._pantalla = FormularioAEDDesign(self.cuerpo_principal, self)
        if nuevo:
            self._pantalla.nuevoContacto()

    def abrirGraficos(self):
        self._activar("graficos")
        self._pantalla = FormularioGraficosDesign(self.cuerpo_principal, self)

    def limpiarPanel(self, panel):
        for widget in panel.winfo_children():
            widget.destroy()
