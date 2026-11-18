"""Pantalla 'Escritorio': resumen de la agenda."""
import tkinter as tk

import util.util_imagenes as util_img
import util.util_ui as ui
from conf import (ACENTO, ACENTO_SUAVE, AUTOR_NOMBRE, CATEGORIAS, FONDO,
                  SUPERFICIE, SUPERFICIE_HOVER, TEXTO, TEXTO_SUAVE, TEXTO_TENUE,
                  estilo_categoria)
from util.util_agenda import cargar_contactos, contar_por_categoria, iniciales
from util.util_ui import Avatar, Boton, InsigniaIcono, Tarjeta, fuente, px


class FormularioEscritorioDesign():
    def __init__(self, panel_escritorio, app=None):
        self.panel = panel_escritorio
        self.app = app
        self.contactos = cargar_contactos()
        self.cuenta = contar_por_categoria(self.contactos, CATEGORIAS)
        total = len(self.contactos)

        nombre = AUTOR_NOMBRE.split()[0]
        acciones, _ = ui.cabecera(panel_escritorio, f"Hola, {nombre}",
                                  f"{ui.fecha_hoy()} · Este es el resumen de tu agenda")
        Boton(acciones, "Nuevo contacto", self._nuevo, "primario", "mas", FONDO).pack()

        # ---------------- Fila de indicadores ----------------
        fila = tk.Frame(panel_escritorio, bg=FONDO)
        fila.pack(fill="x")
        indicadores = [("Contactos", total, "contactos", ACENTO_SUAVE, ACENTO,
                        "en tu agenda")]
        for categoria, estilo in CATEGORIAS.items():
            n = self.cuenta[categoria]
            porcentaje = round(n * 100 / total) if total else 0
            indicadores.append((categoria, n, estilo["icono"], estilo["tinte"],
                                estilo["texto"], f"{porcentaje}% del total"))

        for i, (titulo, valor, icono, fondo, color, pie) in enumerate(indicadores):
            fila.grid_columnconfigure(i, weight=1, uniform="kpi")
            tarjeta = Tarjeta(fila, alto_auto=True, padding=20)
            tarjeta.grid(row=0, column=i, sticky="ew",
                         padx=(0 if i == 0 else px(8), 0 if i == 3 else px(8)))
            c = tarjeta.cuerpo
            arriba = tk.Frame(c, bg=SUPERFICIE)
            arriba.pack(fill="x")
            ui.etiqueta(arriba, titulo, 13.5, "semibold", TEXTO_SUAVE).pack(
                side="left", anchor="n")
            InsigniaIcono(arriba, icono, fondo, color, 36).pack(side="right")
            ui.etiqueta(c, str(valor), 34, "semibold", TEXTO).pack(anchor="w",
                                                                   pady=(px(2), 0))
            ui.etiqueta(c, pie, 12.5, color=TEXTO_TENUE).pack(anchor="w")

        # ---------------- Fila inferior ----------------
        abajo = tk.Frame(panel_escritorio, bg=FONDO)
        abajo.pack(fill="both", expand=True, pady=(px(16), 0))
        abajo.grid_columnconfigure(0, weight=3, uniform="abajo")
        abajo.grid_columnconfigure(1, weight=2, uniform="abajo")
        abajo.grid_rowconfigure(0, weight=1)

        recientes = Tarjeta(abajo, padding=22)
        recientes.grid(row=0, column=0, sticky="nsew", padx=(0, px(8)))
        self._recientes(recientes.cuerpo)

        distribucion = Tarjeta(abajo, padding=22)
        distribucion.grid(row=0, column=1, sticky="nsew", padx=(px(8), 0))
        self._distribucion(distribucion.cuerpo, total)

    def _nuevo(self):
        if self.app:
            self.app.abrirAEDContactos(nuevo=True)

    def _ver_todos(self):
        if self.app:
            self.app.abrirAEDContactos()

    # ------------------------------------------------------------------
    def _titulo_tarjeta(self, padre, titulo, subtitulo, accion=None):
        barra = tk.Frame(padre, bg=SUPERFICIE)
        barra.pack(fill="x", pady=(0, px(12)))
        textos = tk.Frame(barra, bg=SUPERFICIE)
        textos.pack(side="left")
        ui.etiqueta(textos, titulo, 16, "semibold", TEXTO).pack(anchor="w")
        ui.etiqueta(textos, subtitulo, 13, color=TEXTO_SUAVE).pack(anchor="w")
        if accion:
            Boton(barra, accion[0], accion[1], "secundario", alto=34, tam=12.5).pack(
                side="right", anchor="n")

    def _recientes(self, c):
        self._titulo_tarjeta(c, "Añadidos recientemente",
                             "Los últimos contactos que has guardado",
                             ("Ver todos", self._ver_todos) if self.contactos else None)
        if not self.contactos:
            ui.estado_vacio(c, "contactos", "Aún no tienes contactos",
                            "Añade tu primer contacto para empezar a llenar tu agenda.",
                            boton=("Añadir contacto", self._nuevo)).place(
                relx=0.5, rely=0.55, anchor="center")
            return

        # Mostramos tantas filas como quepan en la tarjeta
        lista = tk.Frame(c, bg=SUPERFICIE)
        lista.pack(fill="both", expand=True)
        lista.pack_propagate(False)
        bloques = []
        for contacto in list(reversed(self.contactos))[:10]:
            bloque = tk.Frame(lista, bg=SUPERFICIE)
            ui.separador(bloque)
            self._fila_contacto(bloque, contacto)
            bloques.append(bloque)

        def ajustar(evento):
            usado = 0
            for bloque in bloques:
                usado += bloque.winfo_reqheight()
                if usado <= evento.height:
                    if not bloque.winfo_ismapped():
                        bloque.pack(fill="x")
                else:
                    bloque.pack_forget()

        lista.bind("<Configure>", ajustar)

    def _fila_contacto(self, padre, contacto):
        estilo = estilo_categoria(contacto["categoria"])
        fila = tk.Frame(padre, bg=SUPERFICIE, cursor="hand2")
        fila.pack(fill="x")
        interior = tk.Frame(fila, bg=SUPERFICIE)
        interior.pack(fill="x", padx=px(6), pady=px(9))
        avatar = Avatar(interior, iniciales(contacto["nombre"]), 36, estilo["tinte"],
                        estilo["texto"])
        avatar.pack(side="left")
        insignia = ui.insignia_categoria(interior, contacto["categoria"], estilo)
        insignia.pack(side="right")
        telefono = ui.etiqueta(interior, contacto["telefono"], 13, color=TEXTO_SUAVE)
        telefono.pack(side="right", padx=(0, px(18)))
        textos = tk.Frame(interior, bg=SUPERFICIE)
        textos.pack(side="left", fill="x", expand=True, padx=(px(12), px(8)))
        nombre = ui.etiqueta_recortable(textos, contacto["nombre"], 14, "semibold", TEXTO)
        nombre.pack(fill="x")
        detalle = ui.etiqueta_recortable(textos, contacto["email"], 12.5, color=TEXTO_SUAVE)
        detalle.pack(fill="x")

        widgets = [fila, interior, avatar, textos, nombre, detalle, insignia, telefono]

        def color(fondo):
            for w in widgets:
                w.configure(bg=fondo)

        for w in widgets:
            w.bind("<Enter>", lambda e: color(SUPERFICIE_HOVER))
            w.bind("<Leave>", lambda e: color(SUPERFICIE))
            w.bind("<Button-1>", lambda e, ct=contacto: self._abrir(ct))

    def _abrir(self, contacto):
        if self.app:
            self.app.abrirAEDContactos()
            self.app._pantalla.seleccionarContacto(contacto)

    def _distribucion(self, c, total):
        self._titulo_tarjeta(c, "Por categoría", "Cómo se reparten tus contactos")
        for categoria, estilo in CATEGORIAS.items():
            n = self.cuenta[categoria]
            bloque = tk.Frame(c, bg=SUPERFICIE)
            bloque.pack(fill="x", pady=(px(10), px(6)))
            linea = tk.Frame(bloque, bg=SUPERFICIE)
            linea.pack(fill="x")
            punto = tk.Canvas(linea, width=px(10), height=px(10), bg=SUPERFICIE,
                              highlightthickness=0, bd=0)
            punto._i = util_img.circulo(px(10), estilo["color"])
            punto.create_image(0, 0, anchor="nw", image=punto._i)
            punto.pack(side="left", padx=(0, px(8)))
            ui.etiqueta(linea, categoria, 14, "semibold", TEXTO).pack(side="left")
            porcentaje = (n * 100 / total) if total else 0
            ui.etiqueta(linea, f"{round(porcentaje)}%", 13, color=TEXTO_TENUE).pack(
                side="right")
            ui.etiqueta(linea, f"{n} contacto{'s' if n != 1 else ''}", 13.5,
                        color=TEXTO_SUAVE).pack(side="right", padx=(0, px(10)))
            barra = BarraProgreso(bloque, porcentaje / 100, estilo["color"])
            barra.pack(fill="x", pady=(px(8), 0))


class BarraProgreso(tk.Canvas):
    def __init__(self, padre, fraccion, color, fondo="#f2f4f7"):
        super().__init__(padre, height=px(8), bg=SUPERFICIE, highlightthickness=0, bd=0)
        self.fraccion, self.color, self.fondo = fraccion, color, fondo
        self.bind("<Configure>", lambda e: self._dibujar(e.width))

    def _dibujar(self, w):
        self.delete("all")
        h = px(8)
        self._pista = util_img.rect_redondeado(w, h, h // 2, self.fondo)
        self.create_image(0, 0, anchor="nw", image=self._pista)
        relleno = int(w * self.fraccion)
        if relleno >= h:
            self._barra = util_img.rect_redondeado(relleno, h, h // 2, self.color)
            self.create_image(0, 0, anchor="nw", image=self._barra)
