"""Pantalla 'Gráficos': contactos por categoría.

Los gráficos se dibujan dentro de la propia aplicación. Si la librería
plotly está instalada, también se puede abrir el gráfico interactivo
en el navegador (como en la versión anterior).
"""
import math
import tkinter as tk

import util.util_imagenes as util_img
import util.util_ui as ui
from conf import (BORDE, CATEGORIAS, FONDO, SUPERFICIE, TEXTO, TEXTO_SUAVE,
                  TEXTO_TENUE)
from formularios.form_alertas import mostrar_toast
from util.util_agenda import cargar_contactos, contar_por_categoria
from util.util_ui import Boton, Tarjeta, fuente, px, seguro

try:
    import plotly.express as px_plotly
except ImportError:  # plotly es opcional
    px_plotly = None


class FormularioGraficosDesign():
    def __init__(self, panel_escritorio, app=None):
        self.panel = panel_escritorio
        self.contactos = cargar_contactos()
        self.cuenta = contar_por_categoria(self.contactos, CATEGORIAS)
        self.total = len(self.contactos)

        acciones, _ = ui.cabecera(panel_escritorio, "Gráficos",
                                  "Cómo se distribuyen tus contactos por categoría")
        if px_plotly is not None:
            Boton(acciones, "Abrir en el navegador", self.abrirPlotly, "secundario",
                  "externo", FONDO).pack()

        cuerpo = tk.Frame(panel_escritorio, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=3, uniform="g")
        cuerpo.grid_columnconfigure(1, weight=2, uniform="g")
        cuerpo.grid_rowconfigure(0, weight=1)

        barras = Tarjeta(cuerpo, padding=24)
        barras.grid(row=0, column=0, sticky="nsew", padx=(0, px(8)))
        self._titulo(barras.cuerpo, "Contactos por categoría", "Número de contactos en cada grupo")
        GraficoBarras(barras.cuerpo, self.cuenta).pack(fill="both", expand=True)

        anillo = Tarjeta(cuerpo, padding=24)
        anillo.grid(row=0, column=1, sticky="nsew", padx=(px(8), 0))
        self._titulo(anillo.cuerpo, "Reparto", "Porcentaje sobre el total")
        self._leyenda(anillo.cuerpo)
        GraficoAnillo(anillo.cuerpo, self.cuenta, self.total).pack(fill="both", expand=True)

    def _titulo(self, padre, titulo, subtitulo):
        ui.etiqueta(padre, titulo, 16, "semibold", TEXTO).pack(anchor="w")
        ui.etiqueta(padre, subtitulo, 13, color=TEXTO_SUAVE).pack(anchor="w",
                                                                 pady=(0, px(10)))

    def _leyenda(self, padre):
        leyenda = tk.Frame(padre, bg=SUPERFICIE)
        leyenda.pack(side="bottom", fill="x", pady=(px(12), 0))
        for categoria, estilo in CATEGORIAS.items():
            n = self.cuenta[categoria]
            ui.separador(leyenda)
            fila = tk.Frame(leyenda, bg=SUPERFICIE)
            fila.pack(fill="x", pady=px(10))
            punto = tk.Canvas(fila, width=px(10), height=px(10), bg=SUPERFICIE,
                              highlightthickness=0, bd=0)
            punto._i = util_img.circulo(px(10), estilo["color"])
            punto.create_image(0, 0, anchor="nw", image=punto._i)
            punto.pack(side="left", padx=(px(2), px(10)))
            ui.etiqueta(fila, categoria, 14, "semibold", TEXTO).pack(side="left")
            pct = round(n * 100 / self.total) if self.total else 0
            ui.etiqueta(fila, f"{pct}%", 13.5, color=TEXTO_TENUE, width=5,
                        anchor="e").pack(side="right")
            ui.etiqueta(fila, str(n), 14, "semibold", TEXTO).pack(side="right")

    def abrirPlotly(self):
        """Gráfico interactivo en el navegador (funcionalidad original)."""
        if not self.total:
            mostrar_toast(self.panel, "No hay contactos para mostrar", "error")
            return
        data = {'Categoría': list(CATEGORIAS),
                'Cantidad': [self.cuenta[c] for c in CATEGORIAS]}
        fig = px_plotly.bar(data, x='Categoría', y='Cantidad', color='Categoría',
                            title='Gráfico de Categorías',
                            color_discrete_sequence=[e["color"] for e in CATEGORIAS.values()])
        fig.update_layout(template="plotly_white", showlegend=False)
        fig.show()


class GraficoBarras(tk.Canvas):
    """Gráfico de barras verticales con animación de entrada."""

    def __init__(self, padre, cuenta):
        super().__init__(padre, bg=SUPERFICIE, highlightthickness=0, bd=0)
        self.cuenta = cuenta
        self.progreso = 0.0
        self._imgs = []
        self.bind("<Configure>", lambda e: self.dibujar())
        self.after(120, self._animar)

    @seguro
    def _animar(self, paso=0):
        pasos = 18
        t = paso / pasos
        self.progreso = 1 - (1 - t) ** 3  # ease-out
        self.dibujar()
        if paso < pasos:
            self.after(16, self._animar, paso + 1)

    def dibujar(self):
        self.delete("all")
        self._imgs = []
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50 or h < 80:
            return
        maximo = max(self.cuenta.values()) if self.cuenta else 0
        paso = _paso_bonito(maximo)
        tope = max(paso * 4, math.ceil(maximo / paso) * paso)

        f_eje = fuente(12)
        izq = px(16) + ui.medir(str(tope), f_eje)
        arriba, abajo = px(28), px(40)
        alto_util = h - arriba - abajo

        # Líneas de referencia y valores del eje
        for v in range(0, tope + 1, paso):
            y = arriba + alto_util - alto_util * v / tope
            self.create_line(izq, y, w, y, fill=BORDE if v else "#d0d5dd",
                             dash=() if v == 0 else (3, 4))
            self.create_text(izq - px(10), y, text=str(v), anchor="e", font=f_eje,
                             fill=TEXTO_TENUE)

        # Barras
        n = len(self.cuenta)
        hueco = (w - izq) / n
        ancho_barra = min(px(88), int(hueco * 0.46))
        for i, (categoria, valor) in enumerate(self.cuenta.items()):
            estilo = CATEGORIAS[categoria]
            cx = izq + hueco * (i + 0.5)
            alto_barra = int(alto_util * valor / tope * self.progreso)
            base = arriba + alto_util
            if alto_barra >= 2:
                barra = util_img.rect_redondeado(
                    ancho_barra, alto_barra, min(px(8), alto_barra // 2), estilo["color"],
                    esquinas=(True, True, False, False))
                self._imgs.append(barra)
                self.create_image(cx, base, anchor="s", image=barra)
            self.create_text(cx, base - alto_barra - px(12), text=str(valor),
                             font=fuente(14, "semibold"), fill=TEXTO)
            self.create_text(cx, base + px(20), text=categoria,
                             font=fuente(13, "semibold"), fill=TEXTO_SUAVE)


class GraficoAnillo(tk.Canvas):
    """Gráfico de anillo con el total en el centro."""

    def __init__(self, padre, cuenta, total):
        super().__init__(padre, bg=SUPERFICIE, highlightthickness=0, bd=0)
        self.cuenta, self.total = cuenta, total
        self.bind("<Configure>", lambda e: self.dibujar())

    def dibujar(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        lado = min(w, h, px(240)) - px(8)
        if lado < 60:
            return
        valores = [self.cuenta[c] for c in CATEGORIAS]
        colores = [e["color"] for e in CATEGORIAS.values()]
        self._img = util_img.donut(lado, valores, colores, max(px(18), lado // 8))
        self.create_image(w // 2, h // 2, image=self._img)
        self.create_text(w // 2, h // 2 - px(10), text=str(self.total),
                         font=fuente(max(22, lado / ui.ESCALA / 6), "semibold"), fill=TEXTO)
        self.create_text(w // 2, h // 2 + px(18),
                         text="contacto" if self.total == 1 else "contactos",
                         font=fuente(13), fill=TEXTO_SUAVE)


def _paso_bonito(maximo):
    """Intervalo 'redondo' para el eje (1, 2, 5, 10, 20, 50...)."""
    if maximo <= 4:
        return 1
    bruto = maximo / 4
    magnitud = 10 ** math.floor(math.log10(bruto))
    for m in (1, 2, 5, 10):
        if bruto <= m * magnitud:
            return int(m * magnitud)
    return int(10 * magnitud)
