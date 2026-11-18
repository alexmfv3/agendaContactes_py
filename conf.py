"""Configuración visual y rutas de la aplicación.

Todos los colores de la interfaz se definen aquí para poder
cambiar el aspecto de la app desde un único sitio.
"""
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas (independientes de la carpeta desde la que se ejecute la app)
# ---------------------------------------------------------------------------
EJECUTABLE = getattr(sys, "frozen", False)   # True si se ejecuta como .exe


def _carpeta_datos():
    """Carpeta donde se guarda la agenda.

    - Con 'python main.py': la carpeta del proyecto (como siempre).
    - Como .exe: la carpeta donde está el .exe (versión portable). Si ahí no
      se puede escribir (p. ej. en Archivos de programa), se usa
      %APPDATA%/AgendaContactos.
    """
    if not EJECUTABLE:
        return Path(__file__).resolve().parent
    junto_al_exe = Path(sys.executable).resolve().parent
    try:
        (junto_al_exe / "libreta").mkdir(exist_ok=True)
        prueba = junto_al_exe / "libreta" / ".prueba"
        prueba.write_text("ok")
        prueba.unlink()
        return junto_al_exe
    except OSError:
        base = Path(os.environ.get("APPDATA", Path.home())) / "AgendaContactos"
        base.mkdir(parents=True, exist_ok=True)
        return base


# Las imágenes van dentro del .exe (PyInstaller las descomprime en _MEIPASS)
RUTA_RECURSOS = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
RUTA_BASE = _carpeta_datos()
RUTA_IMAGENES = RUTA_RECURSOS / "imagenes"
RUTA_AGENDA = RUTA_BASE / "libreta" / "agenda.json"

# ---------------------------------------------------------------------------
# Información de la aplicación
# ---------------------------------------------------------------------------
APP_NOMBRE = "Agenda de Contactos"
APP_VERSION = "2.0"
AUTOR_NOMBRE = "Alex Maluquer"
AUTOR_EMAIL = "alex@alexmf.cat"

# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------
FONDO = "#f4f5f7"            # Fondo general de la ventana
SUPERFICIE = "#ffffff"       # Tarjetas, menú lateral, campos
SUPERFICIE_HOVER = "#f8f9fb"
BORDE = "#e7e9ee"
BORDE_FUERTE = "#d0d5dd"

TEXTO = "#101828"
TEXTO_SECUNDARIO = "#475467"
TEXTO_SUAVE = "#667085"
TEXTO_TENUE = "#98a2b3"

ACENTO = "#4f46e5"
ACENTO_HOVER = "#4338ca"
ACENTO_SUAVE = "#eef0ff"
ACENTO_TINTE = "#c7cbfb"

PELIGRO = "#d92d20"
PELIGRO_HOVER = "#fee4e2"
PELIGRO_SUAVE = "#fef3f2"
PELIGRO_BORDE = "#fecdca"

EXITO = "#12b76a"
OSCURO = "#101828"           # Notificaciones (toasts)

# ---------------------------------------------------------------------------
# Categorías de contacto: cada una con su color
#   color  -> color principal (puntos, barras, gráficos)
#   suave  -> fondo de etiquetas
#   tinte  -> fondo de avatares
#   texto  -> texto sobre fondo suave/tinte
# ---------------------------------------------------------------------------
CATEGORIAS = {
    "Amigos": {
        "color": "#f79009", "suave": "#fffaeb", "tinte": "#fef0c7",
        "texto": "#b54708", "icono": "amigos",
    },
    "Trabajo": {
        "color": "#2e90fa", "suave": "#eff8ff", "tinte": "#d1e9ff",
        "texto": "#175cd3", "icono": "trabajo",
    },
    "Familia": {
        "color": "#ee46bc", "suave": "#fdf2fa", "tinte": "#fce7f6",
        "texto": "#c11574", "icono": "familia",
    },
}

CATEGORIA_DESCONOCIDA = {
    "color": "#98a2b3", "suave": "#f2f4f7", "tinte": "#eaecf0",
    "texto": "#475467", "icono": "etiqueta",
}


def estilo_categoria(nombre):
    """Devuelve los colores de una categoría (o unos neutros si no existe)."""
    return CATEGORIAS.get(nombre, CATEGORIA_DESCONOCIDA)
