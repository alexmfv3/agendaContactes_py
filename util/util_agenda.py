"""Lectura y escritura de la agenda (libreta/agenda.json).

El formato del archivo es el mismo que en la versión anterior:
una lista de diccionarios con las claves nombre, telefono, email y categoria.
"""
import json
import re
import shutil

from conf import RUTA_AGENDA

CAMPOS = ("nombre", "telefono", "email", "categoria")
_PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PATRON_TELEFONO = re.compile(r"^\+?[\d\s\-().]{6,}$")


def cargar_contactos():
    """Devuelve la lista de contactos. Si el archivo no existe o está dañado,
    lo crea vacío (guardando antes una copia del archivo dañado)."""
    try:
        datos = json.loads(RUTA_AGENDA.read_text(encoding="utf-8") or "[]")
        if not isinstance(datos, list):
            raise ValueError("Formato no válido")
    except FileNotFoundError:
        guardar_contactos([])
        return []
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        # No perdemos los datos: copiamos el archivo dañado antes de vaciarlo
        try:
            shutil.copy(RUTA_AGENDA, RUTA_AGENDA.with_suffix(".json.bak"))
        except OSError:
            pass
        guardar_contactos([])
        return []

    contactos = []
    for c in datos:
        if isinstance(c, dict):
            contactos.append({campo: str(c.get(campo, "")) for campo in CAMPOS})
    return contactos


def guardar_contactos(contactos):
    """Guarda la lista completa de contactos en el archivo JSON."""
    RUTA_AGENDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_AGENDA.write_text(
        json.dumps(contactos, indent=4, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def validar_contacto(datos):
    """Devuelve un diccionario {campo: mensaje} con los errores encontrados."""
    errores = {}
    if not datos["nombre"]:
        errores["nombre"] = "El nombre no puede estar vacío."
    if not datos["telefono"]:
        errores["telefono"] = "El teléfono no puede estar vacío."
    elif not _PATRON_TELEFONO.match(datos["telefono"]):
        errores["telefono"] = "Introduce un teléfono válido."
    if not datos["email"]:
        errores["email"] = "El email no puede estar vacío."
    elif not _PATRON_EMAIL.match(datos["email"]):
        errores["email"] = "Introduce un email válido."
    if not datos["categoria"]:
        errores["categoria"] = "Elige una categoría."
    return errores


def iniciales(nombre):
    """'Alex Maluquer' -> 'AM'."""
    partes = [p for p in nombre.split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def contar_por_categoria(contactos, categorias):
    cuenta = {cat: 0 for cat in categorias}
    for c in contactos:
        if c["categoria"] in cuenta:
            cuenta[c["categoria"]] += 1
    return cuenta
