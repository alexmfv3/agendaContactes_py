"""Pantalla 'Contactos': Añadir, Editar y Eliminar (A/E/D).

A la izquierda está el listado (con buscador y filtros por categoría)
y a la derecha la ficha del contacto, que sirve tanto para crear uno
nuevo como para editar el que esté seleccionado.
"""
import tkinter as tk
import unicodedata

import util.util_ui as ui
from conf import (ACENTO, ACENTO_SUAVE, CATEGORIAS, FONDO, PELIGRO, SUPERFICIE,
                  SUPERFICIE_HOVER, TEXTO, TEXTO_SECUNDARIO, TEXTO_SUAVE,
                  TEXTO_TENUE, estilo_categoria)
from formularios.form_alertas import confirmar, mostrar_toast
from util.util_agenda import (cargar_contactos, guardar_contactos, iniciales,
                              validar_contacto)
from util.util_ui import (Avatar, Boton, Campo, Pildora, Tarjeta, ZonaScroll,
                          fuente, px)


def _normalizar(texto):
    """Minúsculas y sin acentos, para buscar y ordenar."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


class FormularioAEDDesign():
    def __init__(self, panel_escritorio, app=None):
        self.panel_escritorio = panel_escritorio
        self.app = app
        self.contenido = cargar_contactos()
        self.indiceEditable = None      # None = estamos creando un contacto nuevo
        self.filtro = "Todos"
        self.filas = {}

        acciones, self.etiquetaSubtitulo = ui.cabecera(
            panel_escritorio, "Contactos", self._textoSubtitulo())
        Boton(acciones, "Nuevo contacto", self.nuevoContacto, "primario", "mas",
              FONDO).pack()

        cuerpo = tk.Frame(panel_escritorio, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=0, minsize=px(380))
        cuerpo.grid_rowconfigure(0, weight=1)

        tarjetaLista = Tarjeta(cuerpo, padding=8)
        tarjetaLista.grid(row=0, column=0, sticky="nsew", padx=(0, px(16)))
        self._construirLista(tarjetaLista.cuerpo)

        tarjetaFicha = Tarjeta(cuerpo, padding=24, width=px(380))
        tarjetaFicha.grid(row=0, column=1, sticky="nsew")
        self._construirFicha(tarjetaFicha.cuerpo)

        self.recargarTabla()
        self.nuevoContacto(enfocar=False)

    # ==================================================================
    # Listado
    # ==================================================================
    def _construirLista(self, c):
        arriba = tk.Frame(c, bg=SUPERFICIE, padx=px(12), pady=px(10))
        arriba.pack(fill="x")
        self.campoBuscar = Campo(arriba, icono="buscar",
                                 placeholder="Buscar por nombre, teléfono o email…",
                                 al_cambiar=self.recargarTabla)
        self.campoBuscar.pack(fill="x")
        self.campoBuscar.entry.bind("<Escape>", lambda e: self.campoBuscar.limpiar())

        filtros = tk.Frame(arriba, bg=SUPERFICIE)
        filtros.pack(fill="x", pady=(px(12), 0))
        self.pildorasFiltro = {}
        opciones = [("Todos", None, None)] + [
            (cat, est["color"], est) for cat, est in CATEGORIAS.items()]
        for nombre, punto, estilo in opciones:
            kwargs = {}
            if estilo:
                kwargs = dict(sel_fondo=estilo["suave"], sel_borde=estilo["color"],
                              sel_texto=estilo["texto"])
            p = Pildora(filtros, nombre, lambda n=nombre: self._filtrar(n),
                        seleccionada=(nombre == self.filtro), punto=punto, alto=30,
                        tam=12.5, **kwargs)
            p.pack(side="left", padx=(0, px(6)))
            self.pildorasFiltro[nombre] = p

        ui.separador(c, pady=(px(6), 0))

        self.etiquetaPie = ui.etiqueta(c, "", 12.5, color=TEXTO_TENUE, anchor="w")
        self.etiquetaPie.pack(side="bottom", fill="x", padx=px(14), pady=(px(8), px(4)))
        ui.separador(c, side="bottom")

        self.zona = ZonaScroll(c)
        self.zona.pack(fill="both", expand=True, pady=(px(4), px(4)))

    def _filtrar(self, nombre):
        self.filtro = nombre
        for n, p in self.pildorasFiltro.items():
            p.seleccionar(n == nombre)
        self.recargarTabla()

    def _contactosVisibles(self):
        busqueda = _normalizar(self.campoBuscar.get())
        visibles = []
        for indice, contacto in enumerate(self.contenido):
            if self.filtro != "Todos" and contacto["categoria"] != self.filtro:
                continue
            if busqueda:
                texto = _normalizar(" ".join(contacto.values()))
                if busqueda not in texto:
                    continue
            visibles.append((indice, contacto))
        visibles.sort(key=lambda t: _normalizar(t[1]["nombre"]))
        return visibles

    def recargarTabla(self):
        """Vuelve a dibujar el listado aplicando búsqueda y filtro."""
        for w in self.zona.contenido.winfo_children():
            w.destroy()
        self.filas = {}

        # Contadores de las píldoras de filtro
        self.pildorasFiltro["Todos"].actualizar(contador=len(self.contenido))
        for cat in CATEGORIAS:
            n = sum(1 for c in self.contenido if c["categoria"] == cat)
            self.pildorasFiltro[cat].actualizar(contador=n)

        self.zona.arriba()
        visibles = self._contactosVisibles()
        if not visibles:
            if self.contenido:
                caja = ui.estado_vacio(self.zona.contenido, "buscar", "Sin resultados",
                                       "No hay contactos que coincidan con la búsqueda "
                                       "o el filtro seleccionado.")
            else:
                caja = ui.estado_vacio(self.zona.contenido, "contactos",
                                       "Tu agenda está vacía",
                                       "Rellena la ficha de la derecha para añadir "
                                       "tu primer contacto.")
            caja.pack(pady=px(70))
        else:
            letra_actual = None
            for indice, contacto in visibles:
                letra = (_normalizar(contacto["nombre"])[:1] or "#").upper()
                if not letra.isalpha():
                    letra = "#"
                if letra != letra_actual:
                    letra_actual = letra
                    ui.etiqueta(self.zona.contenido, letra, 12, "semibold", TEXTO_TENUE,
                                anchor="w").pack(fill="x", padx=px(14),
                                                 pady=(px(10), px(2)))
                fila = FilaContacto(self.zona.contenido, contacto,
                                    lambda i=indice: self.editContacto(i),
                                    seleccionada=(indice == self.indiceEditable))
                fila.pack(fill="x", padx=px(4))
                self.filas[indice] = fila

        total = len(self.contenido)
        self.etiquetaPie.configure(
            text=f"Mostrando {len(visibles)} de {total} contacto{'s' if total != 1 else ''}")

    # ==================================================================
    # Ficha (formulario)
    # ==================================================================
    def _construirFicha(self, c):
        # Cabecera de la ficha con avatar
        cab = tk.Frame(c, bg=SUPERFICIE)
        cab.pack(fill="x")
        self.avatar = Avatar(cab, "+", 56, ACENTO_SUAVE, ACENTO)
        self.avatar.pack(side="left")
        textos = tk.Frame(cab, bg=SUPERFICIE)
        textos.pack(side="left", fill="x", expand=True, padx=(px(14), 0))
        self.etiquetaTitulo = ui.etiqueta(textos, "", 18, "semibold", TEXTO, anchor="w")
        self.etiquetaTitulo.pack(fill="x")
        self.etiquetaModo = ui.etiqueta(textos, "", 13, color=TEXTO_SUAVE, anchor="w")
        self.etiquetaModo.pack(fill="x", pady=(px(2), 0))

        ui.separador(c, pady=(px(18), px(18)))

        # Pie con los botones (se empaqueta antes para que quede abajo)
        pie = tk.Frame(c, bg=SUPERFICIE)
        pie.pack(side="bottom", fill="x")
        ui.separador(pie, pady=(0, px(16)))
        botones = tk.Frame(pie, bg=SUPERFICIE)
        botones.pack(fill="x")
        self.botonAdd = Boton(botones, "Añadir contacto", self.addContacto, "primario", "mas")
        self.botonAdd.pack(side="right")
        self.botonCancelar = Boton(botones, "Limpiar", self.nuevoContacto, "secundario")
        self.botonCancelar.pack(side="right", padx=(0, px(10)))
        self.botonEliminar = Boton(botones, "", self.delContacto, "peligro", "papelera")

        # Campos
        campos = tk.Frame(c, bg=SUPERFICIE)
        campos.pack(fill="x")
        self.entryNombre = Campo(campos, "Nombre", "usuario", "Ej. Laura García",
                                 al_cambiar=self._actualizarCabecera,
                                 al_enter=self.addContacto)
        self.entryNombre.pack(fill="x", pady=(0, px(14)))
        self.entryTelefono = Campo(campos, "Teléfono", "telefono", "Ej. 600 123 456",
                                   al_enter=self.addContacto)
        self.entryTelefono.pack(fill="x", pady=(0, px(14)))
        self.entryEmail = Campo(campos, "Email", "email", "Ej. laura@correo.com",
                                al_enter=self.addContacto)
        self.entryEmail.pack(fill="x", pady=(0, px(14)))

        ui.etiqueta(campos, "Categoría", 12.5, "semibold", TEXTO_SECUNDARIO).pack(
            anchor="w", pady=(0, px(6)))
        filaCat = tk.Frame(campos, bg=SUPERFICIE)
        filaCat.pack(fill="x")
        self.clicked = tk.StringVar(value="")
        self.pildorasCategoria = {}
        for cat, est in CATEGORIAS.items():
            p = Pildora(filaCat, cat, lambda n=cat: self._elegirCategoria(n),
                        icono=est["icono"], sel_fondo=est["suave"],
                        sel_borde=est["color"], sel_texto=est["texto"], alto=38)
            p.pack(side="left", padx=(0, px(8)))
            self.pildorasCategoria[cat] = p
        self.errorCategoria = ui.etiqueta(campos, "", 12, color=PELIGRO)

        for campo in (self.entryNombre, self.entryTelefono, self.entryEmail):
            campo.entry.bind("<Escape>", lambda e: self.nuevoContacto())

    def _elegirCategoria(self, categoria):
        self.clicked.set(categoria)
        for n, p in self.pildorasCategoria.items():
            p.seleccionar(n == categoria)
        self.errorCategoria.pack_forget()
        self._actualizarCabecera()

    def _actualizarCabecera(self):
        nombre = self.entryNombre.get()
        estilo = estilo_categoria(self.clicked.get())
        if nombre:
            if self.clicked.get():
                self.avatar.actualizar(iniciales(nombre), estilo["tinte"], estilo["texto"])
            else:
                self.avatar.actualizar(iniciales(nombre), ACENTO_SUAVE, ACENTO)
        else:
            self.avatar.actualizar("+", ACENTO_SUAVE, ACENTO)

        if self.indiceEditable is None:
            titulo = nombre or "Nuevo contacto"
            self.etiquetaModo.configure(text="Rellena los datos del contacto")
        else:
            titulo = nombre or "Sin nombre"
            self.etiquetaModo.configure(text="Editando contacto")
        self.etiquetaTitulo.configure(
            text=ui.recortar(titulo, fuente(18, "semibold"), px(240)))

    def _modoEdicion(self, editando):
        if editando:
            self.botonAdd.configurar("Guardar cambios", "check")
            self.botonCancelar.configurar("Cancelar")
            self.botonEliminar.pack(side="left")
        else:
            self.botonAdd.configurar("Añadir contacto", "mas")
            self.botonCancelar.configurar("Limpiar")
            self.botonEliminar.pack_forget()

    def _marcarFila(self):
        for indice, fila in self.filas.items():
            fila.seleccionar(indice == self.indiceEditable)

    # ==================================================================
    # Acciones: añadir, editar, eliminar
    # ==================================================================
    def limparCampos(self):
        for campo in (self.entryNombre, self.entryTelefono, self.entryEmail):
            campo.limpiar()
        self._elegirCategoria("")
        self.errorCategoria.pack_forget()

    def nuevoContacto(self, enfocar=True):
        """Prepara la ficha para crear un contacto nuevo."""
        self.indiceEditable = None
        self.limparCampos()
        self._modoEdicion(False)
        self._marcarFila()
        self._actualizarCabecera()
        if enfocar:
            self.entryNombre.enfocar()

    def editContacto(self, indice):
        """Carga en la ficha el contacto seleccionado para editarlo."""
        contacto = self.contenido[indice]
        self.indiceEditable = indice
        self.limparCampos()
        self.entryNombre.set(contacto["nombre"])
        self.entryTelefono.set(contacto["telefono"])
        self.entryEmail.set(contacto["email"])
        self._elegirCategoria(contacto["categoria"])
        self._modoEdicion(True)
        self._marcarFila()
        self._actualizarCabecera()

    def seleccionarContacto(self, contacto):
        """Selecciona un contacto a partir de sus datos (desde el Escritorio)."""
        for indice, c in enumerate(self.contenido):
            if c == contacto:
                self.editContacto(indice)
                return

    def addContacto(self):
        """Añade un contacto nuevo o guarda los cambios del que se edita."""
        datos = {
            'nombre': self.entryNombre.get(),
            'telefono': self.entryTelefono.get(),
            'email': self.entryEmail.get(),
            'categoria': self.clicked.get(),
        }
        errores = validar_contacto(datos)
        campos = {"nombre": self.entryNombre, "telefono": self.entryTelefono,
                  "email": self.entryEmail}
        for clave, campo in campos.items():
            if clave in errores:
                campo.mostrar_error(errores[clave])
            else:
                campo.limpiar_error()
        if "categoria" in errores:
            self.errorCategoria.configure(text=errores["categoria"])
            self.errorCategoria.pack(anchor="w", pady=(px(6), 0))
        if errores:
            for clave in ("nombre", "telefono", "email"):
                if clave in errores:
                    campos[clave].enfocar()
                    break
            mostrar_toast(self.panel_escritorio, "Revisa los campos marcados", "error")
            return

        if self.indiceEditable is None:
            self.contenido.append(datos)
            nuevo_indice = len(self.contenido) - 1
            mensaje = "Contacto añadido correctamente"
        else:
            self.contenido[self.indiceEditable] = datos
            nuevo_indice = self.indiceEditable
            mensaje = "Cambios guardados"

        guardar_contactos(self.contenido)
        self._despuesDeCambiar()
        if self.indiceEditable is None:
            self.nuevoContacto()
        else:
            self.editContacto(nuevo_indice)
        self._mostrarFila(nuevo_indice)
        mostrar_toast(self.panel_escritorio, mensaje)

    def delContacto(self):
        """Elimina el contacto seleccionado (pidiendo confirmación)."""
        if self.indiceEditable is None:
            return
        nombre = self.contenido[self.indiceEditable]["nombre"]
        if not confirmar(self.panel_escritorio, "¿Eliminar contacto?",
                         f"Se eliminará a «{nombre}» de tu agenda. "
                         "Esta acción no se puede deshacer."):
            return
        del self.contenido[self.indiceEditable]
        guardar_contactos(self.contenido)
        self.indiceEditable = None
        self._despuesDeCambiar()
        self.nuevoContacto(enfocar=False)
        mostrar_toast(self.panel_escritorio, "Contacto eliminado")

    def _despuesDeCambiar(self):
        self.recargarTabla()
        self.etiquetaSubtitulo.configure(text=self._textoSubtitulo())
        if self.app:
            self.app.actualizarContador()

    def _mostrarFila(self, indice):
        fila = self.filas.get(indice)
        if not fila:
            return
        self.zona.update_idletasks()
        alto_total = max(1, self.zona.contenido.winfo_height())
        y = fila.winfo_y()
        visible_arriba = self.zona.lienzo.canvasy(0)
        visible_abajo = visible_arriba + self.zona.lienzo.winfo_height()
        if y < visible_arriba or y + fila.winfo_height() > visible_abajo:
            self.zona.lienzo.yview_moveto(max(0, (y - px(40)) / alto_total))

    def _textoSubtitulo(self):
        n = len(self.contenido)
        if n == 0:
            return "Tu agenda todavía está vacía"
        return f"{n} contacto{'s' if n != 1 else ''} en tu agenda · selecciona uno para editarlo"


class FilaContacto(tk.Frame):
    """Una fila del listado de contactos."""

    def __init__(self, padre, contacto, comando, seleccionada=False):
        super().__init__(padre, bg=SUPERFICIE, cursor="hand2")
        self.comando = comando
        self.seleccionada = seleccionada
        self._hover = False
        estilo = estilo_categoria(contacto["categoria"])

        self.marca = tk.Frame(self, width=px(3), bg=SUPERFICIE)
        self.marca.pack(side="left", fill="y")
        interior = tk.Frame(self, bg=SUPERFICIE)
        interior.pack(side="left", fill="x", expand=True, padx=(px(9), px(12)),
                      pady=px(9))

        self.avatar = Avatar(interior, iniciales(contacto["nombre"]), 40,
                             estilo["tinte"], estilo["texto"])
        self.avatar.pack(side="left")
        self.insignia = ui.insignia_categoria(interior, contacto["categoria"], estilo)
        self.insignia.pack(side="right")
        textos = tk.Frame(interior, bg=SUPERFICIE)
        textos.pack(side="left", fill="x", expand=True, padx=(px(12), px(10)))
        nombre = ui.etiqueta_recortable(textos, contacto["nombre"], 14, "semibold", TEXTO)
        nombre.pack(fill="x")
        detalle = ui.etiqueta_recortable(
            textos, f"{contacto['telefono']}  ·  {contacto['email']}", 12.5, color=TEXTO_SUAVE)
        detalle.pack(fill="x", pady=(px(1), 0))

        self._fondos = [self, interior, textos, nombre, detalle, self.insignia]
        self._avatarRef = self.avatar
        for w in self._fondos + [self.avatar, self.marca]:
            w.bind("<Enter>", lambda e: self._set_hover(True))
            w.bind("<Leave>", self._salir)
            w.bind("<Button-1>", lambda e: self.comando())
        self._pintar()

    def _salir(self, evento):
        # Solo quitamos el hover si el ratón sale de toda la fila
        x, y = self.winfo_pointerxy()
        w = self.winfo_containing(x, y)
        while w is not None:
            if w is self:
                return
            w = getattr(w, "master", None)
        self._set_hover(False)

    def _set_hover(self, valor):
        if self._hover != valor:
            self._hover = valor
            self._pintar()

    def seleccionar(self, valor):
        self.seleccionada = valor
        self._pintar()

    def _pintar(self):
        if self.seleccionada:
            fondo, marca = ACENTO_SUAVE, ACENTO
        elif self._hover:
            fondo, marca = SUPERFICIE_HOVER, SUPERFICIE_HOVER
        else:
            fondo, marca = SUPERFICIE, SUPERFICIE
        for w in self._fondos:
            w.configure(bg=fondo)
        self.avatar.configure(bg=fondo)
        self.marca.configure(bg=marca)
