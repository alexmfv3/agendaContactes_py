"""Componentes visuales reutilizables.

Tkinter por defecto tiene un aspecto muy básico. Aquí creamos nuestros
propios componentes (tarjetas, botones, campos de texto, etiquetas,
avatares y listas con scroll) dibujándolos sobre un Canvas con imágenes
generadas por Pillow, para conseguir un aspecto moderno.
"""
import sys
import tkinter as tk
from tkinter import font as tkfont

import util.util_imagenes as img
from conf import (ACENTO, ACENTO_HOVER, ACENTO_SUAVE, ACENTO_TINTE, BORDE,
                  BORDE_FUERTE, FONDO, PELIGRO, PELIGRO_BORDE, PELIGRO_HOVER,
                  PELIGRO_SUAVE, SUPERFICIE, SUPERFICIE_HOVER, TEXTO,
                  TEXTO_SECUNDARIO, TEXTO_SUAVE, TEXTO_TENUE)

# ---------------------------------------------------------------------------
# Escala (pantallas de alta resolución) y tipografía
# ---------------------------------------------------------------------------
ESCALA = 1.0
_FAMILIA = "TkDefaultFont"
_FAMILIA_SEMIBOLD = None
_FUENTES = {}
_PREFERIDAS = ("Segoe UI", "Inter", "SF Pro Text", "Helvetica Neue", "Roboto",
               "Ubuntu", "Cantarell", "DejaVu Sans", "Arial", "Helvetica")


def activar_alta_resolucion():
    """En Windows, evita que la app se vea borrosa en pantallas con zoom.
    Debe llamarse antes de crear la ventana principal."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def iniciar(root):
    """Detecta la escala de la pantalla y la mejor fuente disponible."""
    global ESCALA, _FAMILIA, _FAMILIA_SEMIBOLD
    try:
        ESCALA = max(1.0, root.winfo_fpixels("1i") / 96.0)
    except tk.TclError:
        ESCALA = 1.0
    familias = set(tkfont.families(root))
    for f in _PREFERIDAS:
        if f in familias:
            _FAMILIA = f
            break
    if _FAMILIA == "Segoe UI" and "Segoe UI Semibold" in familias:
        _FAMILIA_SEMIBOLD = "Segoe UI Semibold"


def px(valor):
    """Convierte píxeles de diseño a píxeles reales según la escala."""
    return int(round(valor * ESCALA))


def fuente(tamaño, peso="normal"):
    """Fuente con tamaño en píxeles (así encaja siempre con el diseño)."""
    if peso == "semibold":
        if _FAMILIA_SEMIBOLD:
            return (_FAMILIA_SEMIBOLD, -px(tamaño))
        peso = "bold"
    return (_FAMILIA, -px(tamaño), peso)


def _objeto_fuente(f):
    if f not in _FUENTES:
        _FUENTES[f] = tkfont.Font(font=f)
    return _FUENTES[f]


def medir(texto, f):
    return _objeto_fuente(f).measure(texto)


def recortar(texto, f, ancho_max):
    """Recorta un texto con '…' para que quepa en el ancho indicado."""
    if medir(texto, f) <= ancho_max:
        return texto
    while texto and medir(texto + "…", f) > ancho_max:
        texto = texto[:-1]
    return texto.rstrip() + "…"


def seguro(funcion):
    """Ejecuta un callback ignorando errores de widgets ya destruidos."""
    def envoltorio(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except tk.TclError:
            return None
    return envoltorio


def etiqueta(padre, texto, tam=13, peso="normal", color=TEXTO, fondo=SUPERFICIE, **kw):
    return tk.Label(padre, text=texto, font=fuente(tam, peso), fg=color, bg=fondo,
                    bd=0, **kw)


# ---------------------------------------------------------------------------
# Tarjeta: contenedor blanco con esquinas redondeadas y sombra suave
# ---------------------------------------------------------------------------
class Tarjeta(tk.Canvas):
    def __init__(self, padre, fondo_padre=FONDO, color=SUPERFICIE, borde=BORDE,
                 radio=14, padding=20, alto_auto=False, **kw):
        super().__init__(padre, bg=fondo_padre, highlightthickness=0, bd=0, **kw)
        self.color, self.borde = color, borde
        self.radio = px(radio)
        self.margen = px(4)
        self.pad = px(padding) if isinstance(padding, (int, float)) else padding
        self.alto_auto = alto_auto
        self._img = None
        self._pendiente = None

        self._fondo = self.create_image(0, 0, anchor="nw")
        self.cuerpo = tk.Frame(self, bg=color)
        off = self.margen + self.pad
        self._ventana = self.create_window(off, off, window=self.cuerpo, anchor="nw")

        self.bind("<Configure>", self._al_cambiar)
        if alto_auto:
            self.cuerpo.bind("<Configure>", self._ajustar_alto, add="+")

    def _al_cambiar(self, evento):
        off = self.margen + self.pad
        self.itemconfigure(self._ventana, width=max(1, evento.width - 2 * off))
        if not self.alto_auto:
            self.itemconfigure(self._ventana, height=max(1, evento.height - 2 * off))
        if self._pendiente:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(12, self._redibujar)

    @seguro
    def _redibujar(self):
        self._pendiente = None
        w, h = self.winfo_width(), self.winfo_height()
        if w < 8 or h < 8:
            return
        self._img = img.tarjeta(w, h, self.radio, self.color, self.borde, self.margen)
        self.itemconfigure(self._fondo, image=self._img)

    def _ajustar_alto(self, _evento=None):
        alto = self.cuerpo.winfo_reqheight() + 2 * (self.margen + self.pad)
        if getattr(self, "_alto_actual", None) != alto:
            self._alto_actual = alto
            self.configure(height=alto)


# ---------------------------------------------------------------------------
# Botón con esquinas redondeadas, icono opcional y efecto hover
# ---------------------------------------------------------------------------
VARIANTES_BOTON = {
    "primario": dict(fondo=ACENTO, hover=ACENTO_HOVER, texto="#ffffff", borde=None),
    "secundario": dict(fondo=SUPERFICIE, hover="#f2f4f7", texto=TEXTO_SECUNDARIO,
                       borde=BORDE_FUERTE),
    "peligro": dict(fondo=PELIGRO_SUAVE, hover=PELIGRO_HOVER, texto=PELIGRO,
                    borde=PELIGRO_BORDE),
    "peligro_solido": dict(fondo=PELIGRO, hover="#b42318", texto="#ffffff", borde=None),
    "fantasma": dict(fondo=None, hover="#f2f4f7", texto=TEXTO_SUAVE, borde=None),
}


class Boton(tk.Canvas):
    def __init__(self, padre, texto="", comando=None, variante="primario", icono=None,
                 fondo_padre=SUPERFICIE, alto=40, ancho=None, tam=13.5):
        super().__init__(padre, bg=fondo_padre, highlightthickness=0, bd=0,
                         cursor="hand2", takefocus=0)
        self.texto, self.comando, self.icono = texto, comando, icono
        self.variante = VARIANTES_BOTON[variante]
        self.fondo_padre = fondo_padre
        self.alto, self.ancho_fijo = px(alto), (px(ancho) if ancho else None)
        self.f = fuente(tam, "semibold")
        self._hover = False
        self._dibujar()
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._click)

    def _set_hover(self, valor):
        self._hover = valor
        self._dibujar()

    def _click(self, evento):
        if 0 <= evento.x <= self.winfo_width() and 0 <= evento.y <= self.winfo_height():
            if self.comando:
                self.comando()

    def configurar(self, texto=None, icono=None, comando=None):
        if texto is not None:
            self.texto = texto
        if icono is not None:
            self.icono = icono
        if comando is not None:
            self.comando = comando
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        v = self.variante
        fondo = v["hover"] if self._hover else (v["fondo"] or self.fondo_padre)
        tw = medir(self.texto, self.f) if self.texto else 0
        iw = px(17) if self.icono else 0
        hueco = px(8) if (self.icono and self.texto) else 0
        relleno = px(16) if self.texto else (self.alto - iw) // 2
        w = self.ancho_fijo or (tw + iw + hueco + 2 * relleno)
        h = self.alto
        self.configure(width=w, height=h)
        if fondo != self.fondo_padre or v["borde"]:
            self._img = img.rect_redondeado(w, h, px(9), fondo, v["borde"])
            self.create_image(0, 0, anchor="nw", image=self._img)
        x = (w - (tw + iw + hueco)) // 2
        if self.icono:
            self._ico = img.icono(self.icono, iw, v["texto"])
            self.create_image(x, h // 2, anchor="w", image=self._ico)
            x += iw + hueco
        if self.texto:
            self.create_text(x, h // 2, text=self.texto, anchor="w", font=self.f,
                             fill=v["texto"])


# ---------------------------------------------------------------------------
# Campo de texto con etiqueta, icono, placeholder y mensaje de error
# ---------------------------------------------------------------------------
class Campo(tk.Frame):
    def __init__(self, padre, etiqueta_texto=None, icono=None, placeholder="",
                 fondo=SUPERFICIE, alto=42, al_cambiar=None, al_enter=None):
        super().__init__(padre, bg=fondo)
        self.fondo = fondo
        self.alto = px(alto)
        self.icono = icono
        self._estado = "normal"
        self._error = None
        self.al_cambiar = al_cambiar

        if etiqueta_texto:
            etiqueta(self, etiqueta_texto, 12.5, "semibold", TEXTO_SECUNDARIO,
                     fondo).pack(anchor="w", pady=(0, px(6)))

        self.lienzo = tk.Canvas(self, bg=fondo, height=self.alto, highlightthickness=0,
                                bd=0, cursor="xterm")
        self.lienzo.pack(fill="x")
        self._fondo_id = self.lienzo.create_image(0, 0, anchor="nw")

        self.var = tk.StringVar()
        self.entry = tk.Entry(self.lienzo, textvariable=self.var, bd=0, relief="flat",
                              highlightthickness=0, bg=SUPERFICIE, fg=TEXTO,
                              insertbackground=TEXTO, insertwidth=max(1, px(1.5)),
                              selectbackground=ACENTO_TINTE, selectforeground=TEXTO,
                              font=fuente(14))
        self.x0 = px(42) if icono else px(14)
        if icono:
            self._ico_id = self.lienzo.create_image(px(14), self.alto // 2, anchor="w")
        self.placeholder = placeholder
        self._con_placeholder = False
        self._silencio = False
        self._win = self.lienzo.create_window(self.x0, self.alto // 2, anchor="w",
                                              window=self.entry)

        self.etiqueta_error = etiqueta(self, "", 12, color=PELIGRO, fondo=fondo)

        self.lienzo.bind("<Configure>", lambda e: self._dibujar())
        self.lienzo.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.entry.bind("<FocusIn>", self._al_enfocar)
        self.entry.bind("<FocusOut>", self._al_desenfocar)
        if al_enter:
            self.entry.bind("<Return>", lambda e: al_enter())
        self.var.trace_add("write", self._al_escribir)
        self._poner_placeholder()

    # Texto de ejemplo en gris cuando el campo está vacío -----------------
    def _poner_placeholder(self):
        try:
            enfocado = self.focus_get() is self.entry
        except (KeyError, tk.TclError):
            enfocado = False
        if self.placeholder and not self.var.get() and not enfocado:
            self._silencio = True
            self._con_placeholder = True
            self.var.set(self.placeholder)
            self.entry.configure(fg=TEXTO_TENUE)
            self._silencio = False

    def _quitar_placeholder(self):
        if self._con_placeholder:
            self._silencio = True
            self._con_placeholder = False
            self.var.set("")
            self.entry.configure(fg=TEXTO)
            self._silencio = False

    def _al_enfocar(self, _e=None):
        self._quitar_placeholder()
        self._cambiar_estado("foco")

    def _al_desenfocar(self, _e=None):
        self._poner_placeholder()
        self._cambiar_estado("normal")

    def _al_escribir(self, *_):
        if self._silencio:
            return
        if self._error and self.var.get():
            self.limpiar_error()
        if self.al_cambiar:
            self.al_cambiar()

    def _cambiar_estado(self, estado):
        self._estado = estado
        self._dibujar()

    @seguro
    def _dibujar(self):
        w = self.lienzo.winfo_width()
        if w < 10:
            return
        if self._error:
            borde, grosor, color_icono = PELIGRO, 1.5, PELIGRO
        elif self._estado == "foco":
            borde, grosor, color_icono = ACENTO, 1.5, ACENTO
        else:
            borde, grosor, color_icono = BORDE_FUERTE, 1, TEXTO_TENUE
        self._img = img.rect_redondeado(w, self.alto, px(9), SUPERFICIE, borde,
                                        grosor * px(1))
        self.lienzo.itemconfigure(self._fondo_id, image=self._img)
        if self.icono:
            self._ico = img.icono(self.icono, px(18), color_icono)
            self.lienzo.itemconfigure(self._ico_id, image=self._ico)
        self.lienzo.itemconfigure(self._win, width=max(10, w - self.x0 - px(12)))

    # API pública ---------------------------------------------------------
    def get(self):
        if self._con_placeholder:
            return ""
        return self.var.get().strip()

    def set(self, valor):
        self._quitar_placeholder()
        self.var.set(valor)
        if not valor:
            self._poner_placeholder()

    def limpiar(self):
        self.set("")
        self.limpiar_error()

    def enfocar(self):
        self.entry.focus_set()
        self.entry.icursor(tk.END)

    def mostrar_error(self, mensaje):
        self._error = mensaje
        self.etiqueta_error.configure(text=mensaje)
        self.etiqueta_error.pack(anchor="w", pady=(px(5), 0))
        self._dibujar()

    def limpiar_error(self):
        self._error = None
        self.etiqueta_error.pack_forget()
        self._dibujar()


# ---------------------------------------------------------------------------
# Píldora: etiqueta redondeada (seleccionable o estática)
# ---------------------------------------------------------------------------
class Pildora(tk.Canvas):
    def __init__(self, padre, texto, comando=None, seleccionada=False, punto=None,
                 contador=None, fondo_padre=SUPERFICIE, sel_fondo=ACENTO_SUAVE,
                 sel_borde=ACENTO_TINTE, sel_texto=ACENTO, alto=32, tam=13,
                 icono=None, borde=True):
        super().__init__(padre, bg=fondo_padre, highlightthickness=0, bd=0,
                         cursor="hand2" if comando else "")
        self.texto, self.comando, self.punto, self.contador = texto, comando, punto, contador
        self.icono = icono
        self.seleccionada = seleccionada
        self.colores_sel = (sel_fondo, sel_borde, sel_texto)
        self.con_borde = borde
        self.alto = px(alto)
        self.f = fuente(tam, "semibold")
        self.f_contador = fuente(tam - 1)
        self._hover = False
        self._dibujar()
        if comando:
            self.bind("<Enter>", lambda e: self._set_hover(True))
            self.bind("<Leave>", lambda e: self._set_hover(False))
            self.bind("<ButtonRelease-1>", lambda e: self.comando())

    def _set_hover(self, valor):
        self._hover = valor
        self._dibujar()

    def seleccionar(self, valor):
        self.seleccionada = valor
        self._dibujar()

    def actualizar(self, texto=None, contador=None):
        if texto is not None:
            self.texto = texto
        self.contador = contador
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        if self.seleccionada:
            fondo, borde, color = self.colores_sel
            color_contador = color
        else:
            fondo = SUPERFICIE_HOVER if self._hover else SUPERFICIE
            borde, color, color_contador = BORDE_FUERTE, TEXTO_SECUNDARIO, TEXTO_TENUE
        if not self.con_borde:
            borde = None
        pad = px(12) if self.alto > px(32) else (px(10) if self.alto > px(26) else px(9))
        tw = medir(self.texto, self.f)
        dot = px(8) if self.punto else 0
        ico = px(14) if self.icono else 0
        lead = (dot + px(7)) if dot else ((ico + px(6)) if ico else 0)
        ctxt = str(self.contador) if self.contador is not None else ""
        cw = (medir(ctxt, self.f_contador) + px(10)) if ctxt else 0
        w = pad + lead + tw + cw + pad
        h = self.alto
        self.configure(width=w, height=h)
        self._img = img.rect_redondeado(w, h, h // 2, fondo, borde)
        self.create_image(0, 0, anchor="nw", image=self._img)
        x = pad
        if dot:
            self._dot = img.circulo(dot, self.punto)
            self.create_image(x, h // 2, anchor="w", image=self._dot)
        elif ico:
            self._ico = img.icono(self.icono, ico, color)
            self.create_image(x, h // 2, anchor="w", image=self._ico)
        x += lead
        id_texto = self.create_text(x, h // 2, text=self.texto, anchor="w", font=self.f,
                                    fill=color)
        if ctxt:
            caja = self.bbox(id_texto)
            fin = max(x + tw, caja[2] if caja else 0)
            self.create_text(fin + px(6), h // 2, text=ctxt, anchor="w",
                             font=self.f_contador, fill=color_contador)


def insignia_categoria(padre, categoria, estilo, fondo_padre=SUPERFICIE):
    """Etiqueta pequeña con el nombre de la categoría y su color."""
    return Pildora(padre, categoria or "Sin categoría", seleccionada=True,
                   punto=estilo["color"], fondo_padre=fondo_padre,
                   sel_fondo=estilo["suave"], sel_borde=None, sel_texto=estilo["texto"],
                   alto=24, tam=12, borde=False)


# ---------------------------------------------------------------------------
# Avatar circular con iniciales
# ---------------------------------------------------------------------------
class Avatar(tk.Canvas):
    def __init__(self, padre, texto, tam=40, fondo="#eaecf0", color=TEXTO_SECUNDARIO,
                 fondo_padre=SUPERFICIE):
        self.tam = px(tam)
        super().__init__(padre, width=self.tam, height=self.tam, bg=fondo_padre,
                         highlightthickness=0, bd=0)
        self.f = fuente(tam * 0.38, "semibold")
        self.actualizar(texto, fondo, color)

    def actualizar(self, texto, fondo, color):
        self.delete("all")
        self._img = img.circulo(self.tam, fondo)
        self.create_image(0, 0, anchor="nw", image=self._img)
        self.create_text(self.tam / 2, self.tam / 2 + px(0.5), text=texto, font=self.f,
                         fill=color)


class InsigniaIcono(tk.Canvas):
    """Cuadrado redondeado de color con un icono dentro."""

    def __init__(self, padre, icono, fondo, color, tam=40, fondo_padre=SUPERFICIE):
        t = px(tam)
        super().__init__(padre, width=t, height=t, bg=fondo_padre,
                         highlightthickness=0, bd=0)
        self._fondo = img.rect_redondeado(t, t, px(10), fondo)
        self._ico = img.icono(icono, int(t * 0.5), color)
        self.create_image(0, 0, anchor="nw", image=self._fondo)
        self.create_image(t // 2, t // 2, image=self._ico)


# ---------------------------------------------------------------------------
# Zona con scroll vertical (barra fina y rueda del ratón)
# ---------------------------------------------------------------------------
class ZonaScroll(tk.Frame):
    _rueda_registrada = False

    def __init__(self, padre, fondo=SUPERFICIE):
        super().__init__(padre, bg=fondo)
        self.lienzo = tk.Canvas(self, bg=fondo, highlightthickness=0, bd=0,
                                yscrollincrement=px(20))
        self.barra = tk.Canvas(self, bg=fondo, width=px(10), highlightthickness=0, bd=0)
        self.barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.contenido = tk.Frame(self.lienzo, bg=fondo)
        self._win = self.lienzo.create_window(0, 0, anchor="nw", window=self.contenido)
        self._pos = (0.0, 1.0)

        self.contenido.bind("<Configure>", self._al_cambiar_contenido)
        self.lienzo.bind("<Configure>", self._al_cambiar_lienzo)
        self.lienzo.configure(yscrollcommand=self._al_mover)
        self.barra.bind("<B1-Motion>", self._arrastrar)
        self.barra.bind("<Button-1>", self._arrastrar)

        if not ZonaScroll._rueda_registrada:
            raiz = self.winfo_toplevel()
            for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                raiz.bind_all(evento, ZonaScroll._rueda_global, add="+")
            ZonaScroll._rueda_registrada = True

    @staticmethod
    def _rueda_global(evento):
        try:
            w = evento.widget.winfo_containing(evento.x_root, evento.y_root)
        except (tk.TclError, AttributeError, KeyError):
            return
        while w is not None:
            if isinstance(w, ZonaScroll):
                w._rueda(evento)
                return
            w = getattr(w, "master", None)

    def _rueda(self, evento):
        if self._pos == (0.0, 1.0):
            return
        if evento.num == 4:
            pasos = -2
        elif evento.num == 5:
            pasos = 2
        elif sys.platform == "darwin":
            pasos = -evento.delta
        else:
            pasos = -round(evento.delta / 120 * 2) or (-1 if evento.delta > 0 else 1)
        self.lienzo.yview_scroll(pasos, "units")

    def _al_cambiar_contenido(self, _e):
        self.lienzo.configure(scrollregion=self.lienzo.bbox(self._win))

    def _al_cambiar_lienzo(self, e):
        self.lienzo.itemconfigure(self._win, width=e.width)
        self._pintar_barra()

    def _al_mover(self, primero, ultimo):
        self._pos = (float(primero), float(ultimo))
        self._pintar_barra()

    @seguro
    def _pintar_barra(self):
        self.barra.delete("all")
        primero, ultimo = self._pos
        if ultimo - primero >= 0.999:
            return
        h = self.barra.winfo_height()
        y0, y1 = int(primero * h), int(ultimo * h)
        alto = max(px(24), y1 - y0)
        self._thumb = img.rect_redondeado(px(6), alto, px(3), "#d0d5dd")
        self.barra.create_image(px(2), y0, anchor="nw", image=self._thumb)

    def _arrastrar(self, e):
        primero, ultimo = self._pos
        visible = ultimo - primero
        h = max(1, self.barra.winfo_height())
        self.lienzo.yview_moveto(max(0.0, e.y / h - visible / 2))

    def arriba(self):
        self.lienzo.yview_moveto(0)


# ---------------------------------------------------------------------------
# Cabecera común de cada pantalla
# ---------------------------------------------------------------------------
_DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre")


def fecha_hoy():
    import datetime
    hoy = datetime.date.today()
    return f"{_DIAS[hoy.weekday()].capitalize()}, {hoy.day} de {_MESES[hoy.month - 1]} de {hoy.year}"


def cabecera(padre, titulo, subtitulo=""):
    """Crea el título y subtítulo de una pantalla.
    Devuelve (frame_acciones, etiqueta_subtitulo)."""
    barra = tk.Frame(padre, bg=FONDO)
    barra.pack(fill="x", pady=(0, px(20)))
    textos = tk.Frame(barra, bg=FONDO)
    textos.pack(side="left", fill="x", expand=True)
    etiqueta(textos, titulo, 26, "semibold", TEXTO, FONDO).pack(anchor="w")
    sub = etiqueta(textos, subtitulo, 14, color=TEXTO_SUAVE, fondo=FONDO)
    sub.pack(anchor="w", pady=(px(2), 0))
    acciones = tk.Frame(barra, bg=FONDO)
    acciones.pack(side="right", anchor="s")
    return acciones, sub


def estado_vacio(padre, icono, titulo, texto, fondo=SUPERFICIE, boton=None):
    """Mensaje centrado cuando no hay datos que mostrar."""
    caja = tk.Frame(padre, bg=fondo)
    badge = tk.Canvas(caja, width=px(56), height=px(56), bg=fondo,
                      highlightthickness=0, bd=0)
    badge._c = img.circulo(px(56), ACENTO_SUAVE)
    badge._i = img.icono(icono, px(26), ACENTO)
    badge.create_image(0, 0, anchor="nw", image=badge._c)
    badge.create_image(px(28), px(28), image=badge._i)
    badge.pack(pady=(0, px(14)))
    etiqueta(caja, titulo, 15.5, "semibold", TEXTO, fondo).pack()
    etiqueta(caja, texto, 13, color=TEXTO_SUAVE, fondo=fondo, justify="center",
             wraplength=px(280)).pack(pady=(px(4), 0))
    if boton:
        texto_boton, comando = boton
        Boton(caja, texto_boton, comando, "primario", "mas", fondo).pack(pady=(px(16), 0))
    return caja


def separador(padre, color=BORDE, **pack):
    linea = tk.Frame(padre, bg=color, height=max(1, px(1)))
    linea.pack(fill="x", **pack)
    return linea


def etiqueta_recortable(padre, texto, tam=13, peso="normal", color=TEXTO, fondo=SUPERFICIE):
    """Etiqueta que añade '…' si el texto no cabe en el espacio disponible."""
    f = fuente(tam, peso)
    lbl = tk.Label(padre, text=texto, font=f, fg=color, bg=fondo, bd=0, anchor="w",
                   width=1)
    lbl._texto_completo = texto

    def ajustar(evento):
        nuevo = recortar(lbl._texto_completo, f, max(10, evento.width - px(8)))
        if nuevo != lbl.cget("text"):
            lbl.configure(text=nuevo)

    lbl.bind("<Configure>", ajustar, add="+")
    return lbl
