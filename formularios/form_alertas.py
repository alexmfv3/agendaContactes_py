"""Mensajes al usuario: notificaciones flotantes (toasts),
diálogo de confirmación y las ventanas clásicas de aviso."""
import tkinter as tk
from tkinter import messagebox

import util.util_imagenes as img
import util.util_ventana as util_ventana
from conf import (EXITO, OSCURO, PELIGRO, PELIGRO_SUAVE, SUPERFICIE, TEXTO,
                  TEXTO_SUAVE, FONDO, RUTA_IMAGENES)
from util.util_ui import Boton, etiqueta, fuente, medir, px, seguro


class Ventana:
    """Ventanas emergentes clásicas (se mantienen por compatibilidad)."""

    def __init__(self, tipo, titulo, mensaje) -> None:
        if tipo == 'info':
            messagebox.showinfo(titulo, mensaje)
        if tipo == 'error':
            messagebox.showerror(titulo, mensaje)
        if tipo == 'aviso':
            messagebox.showwarning(titulo, mensaje)


# ---------------------------------------------------------------------------
# Toast: notificación pequeña que aparece abajo y desaparece sola
# ---------------------------------------------------------------------------
def mostrar_toast(raiz, mensaje, tipo="exito", duracion=2600):
    raiz = raiz.winfo_toplevel()
    anterior = getattr(raiz, "_toast", None)
    if anterior is not None:
        try:
            anterior.destroy()
        except tk.TclError:
            pass

    f = fuente(13.5, "semibold")
    alto = px(48)
    ancho = px(16) + px(24) + px(12) + medir(mensaje, f) + px(22)
    lienzo = tk.Canvas(raiz, width=ancho, height=alto, bg=FONDO,
                       highlightthickness=0, bd=0)
    lienzo._fondo = img.rect_redondeado(ancho, alto, px(12), OSCURO)
    color = EXITO if tipo == "exito" else PELIGRO
    lienzo._circ = img.circulo(px(24), color)
    lienzo._ico = img.icono("check" if tipo == "exito" else "cerrar", px(14), "#ffffff", 2.6)
    lienzo.create_image(0, 0, anchor="nw", image=lienzo._fondo)
    lienzo.create_image(px(16), alto // 2, anchor="w", image=lienzo._circ)
    lienzo.create_image(px(16) + px(12), alto // 2, image=lienzo._ico)
    lienzo.create_text(px(16) + px(24) + px(12), alto // 2, anchor="w", text=mensaje,
                       font=f, fill="#ffffff")
    raiz._toast = lienzo

    # Pequeña animación de entrada desde abajo
    pasos = 8

    @seguro
    def animar(i=0):
        desplazamiento = int(px(24) * (1 - (i / pasos)) ** 2)
        lienzo.place(relx=0.5, rely=1.0, x=px(124), y=-px(28) + desplazamiento, anchor="s")
        lienzo.lift()
        if i < pasos:
            lienzo.after(16, animar, i + 1)

    animar()
    lienzo.after(duracion, seguro(lienzo.destroy))


# ---------------------------------------------------------------------------
# Diálogo de confirmación con estilo propio
# ---------------------------------------------------------------------------
def confirmar(raiz, titulo, mensaje, texto_ok="Eliminar", icono="papelera"):
    """Muestra un diálogo modal y devuelve True si el usuario confirma."""
    raiz = raiz.winfo_toplevel()
    resultado = {"ok": False}

    dialogo = tk.Toplevel(raiz)
    dialogo.withdraw()
    dialogo.title(titulo)
    dialogo.configure(bg=SUPERFICIE)
    dialogo.resizable(False, False)
    dialogo.transient(raiz)
    try:
        dialogo.iconbitmap(str(RUTA_IMAGENES / "ICON.ico"))
    except tk.TclError:
        pass

    cuerpo = tk.Frame(dialogo, bg=SUPERFICIE, padx=px(24), pady=px(22))
    cuerpo.pack(fill="both", expand=True)

    fila = tk.Frame(cuerpo, bg=SUPERFICIE)
    fila.pack(fill="x")
    badge = tk.Canvas(fila, width=px(44), height=px(44), bg=SUPERFICIE,
                      highlightthickness=0, bd=0)
    badge._c = img.circulo(px(44), PELIGRO_SUAVE)
    badge._i = img.icono(icono, px(20), PELIGRO)
    badge.create_image(0, 0, anchor="nw", image=badge._c)
    badge.create_image(px(22), px(22), image=badge._i)
    badge.pack(side="left", anchor="n", padx=(0, px(16)))

    textos = tk.Frame(fila, bg=SUPERFICIE)
    textos.pack(side="left", fill="x", expand=True)
    etiqueta(textos, titulo, 17, "semibold", TEXTO).pack(anchor="w")
    etiqueta(textos, mensaje, 13.5, color=TEXTO_SUAVE, justify="left",
             wraplength=px(300)).pack(anchor="w", pady=(px(4), 0))

    botones = tk.Frame(cuerpo, bg=SUPERFICIE)
    botones.pack(fill="x", pady=(px(22), 0))

    def cerrar(valor):
        resultado["ok"] = valor
        dialogo.grab_release()
        dialogo.destroy()

    Boton(botones, texto_ok, lambda: cerrar(True), "peligro_solido").pack(side="right")
    Boton(botones, "Cancelar", lambda: cerrar(False), "secundario").pack(
        side="right", padx=(0, px(10)))

    dialogo.bind("<Escape>", lambda e: cerrar(False))
    dialogo.bind("<Return>", lambda e: cerrar(True))
    dialogo.protocol("WM_DELETE_WINDOW", lambda: cerrar(False))

    dialogo.update_idletasks()
    util_ventana.centrarSobre(dialogo, raiz, max(px(420), dialogo.winfo_reqwidth()),
                              dialogo.winfo_reqheight())
    dialogo.deiconify()
    dialogo.grab_set()
    dialogo.focus_set()
    raiz.wait_window(dialogo)
    return resultado["ok"]
