"""Generación de imágenes con Pillow.

Tkinter no sabe dibujar esquinas redondeadas ni formas suavizadas,
así que las dibujamos con Pillow a mayor resolución y las reducimos
(supersampling). Así todo se ve nítido y sin dientes de sierra.
"""
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageFilter, ImageTk

from conf import RUTA_IMAGENES

_CACHE = OrderedDict()
_CACHE_MAX = 400

try:
    _LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # Pillow antiguo
    _LANCZOS = Image.LANCZOS


def _cacheado(clave, crear):
    if clave in _CACHE:
        _CACHE.move_to_end(clave)
        return _CACHE[clave]
    img = crear()
    _CACHE[clave] = img
    if len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)
    return img


def _hex(color, alfa=255):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4)) + (alfa,)


def _ss(w, h):
    """Factor de supersampling: más alto en imágenes pequeñas."""
    return 4 if w * h < 90_000 else 2


def _rect(draw, caja, radio, relleno, esquinas=None):
    try:
        draw.rounded_rectangle(caja, radio, fill=relleno, corners=esquinas)
    except TypeError:  # Pillow < 9.2 no tiene el parámetro corners
        draw.rounded_rectangle(caja, radio, fill=relleno)


# ---------------------------------------------------------------------------
# Imágenes del proyecto
# ---------------------------------------------------------------------------
def leerImagen(ruta, tamaño):
    """Carga una imagen del disco con el tamaño indicado."""
    return ImageTk.PhotoImage(Image.open(ruta).convert("RGBA").resize(tamaño, _LANCZOS))


def logo_app(alto):
    """Logo de la app escalado manteniendo la proporción."""
    def crear():
        img = Image.open(RUTA_IMAGENES / "logoApp.png").convert("RGBA")
        ancho = round(img.width * alto / img.height)
        return ImageTk.PhotoImage(img.resize((ancho, alto), _LANCZOS))
    return _cacheado(("logo", alto), crear)


def imagen_circular(nombre_archivo, tamaño, fondo="#ffffff"):
    """Recorta una imagen en forma de círculo (para la foto de perfil)."""
    def crear():
        ss = 4
        grande = tamaño * ss
        img = Image.open(RUTA_IMAGENES / nombre_archivo).convert("RGBA")
        lado = min(img.size)
        img = img.crop(((img.width - lado) // 2, (img.height - lado) // 2,
                        (img.width + lado) // 2, (img.height + lado) // 2))
        img = img.resize((grande, grande), _LANCZOS)
        base = Image.new("RGBA", (grande, grande), _hex(fondo))
        base.alpha_composite(img)
        mascara = Image.new("L", (grande, grande), 0)
        ImageDraw.Draw(mascara).ellipse((0, 0, grande - 1, grande - 1), fill=255)
        salida = Image.new("RGBA", (grande, grande), (0, 0, 0, 0))
        salida.paste(base, (0, 0), mascara)
        return ImageTk.PhotoImage(salida.resize((tamaño, tamaño), _LANCZOS))
    return _cacheado(("circular", nombre_archivo, tamaño, fondo), crear)


# ---------------------------------------------------------------------------
# Formas
# ---------------------------------------------------------------------------
def rect_redondeado(w, h, radio, relleno, borde=None, grosor=1, esquinas=None):
    """Rectángulo con esquinas redondeadas (opcionalmente con borde)."""
    w, h = max(1, int(w)), max(1, int(h))

    def crear():
        ss = _ss(w, h)
        W, H = w * ss, h * ss
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        r = min(radio * ss, W // 2, H // 2)
        if borde:
            _rect(d, (0, 0, W - 1, H - 1), r, _hex(borde), esquinas)
            g = max(1, round(grosor * ss))
            _rect(d, (g, g, W - 1 - g, H - 1 - g), max(0, r - g), _hex(relleno), esquinas)
        else:
            _rect(d, (0, 0, W - 1, H - 1), r, _hex(relleno), esquinas)
        return ImageTk.PhotoImage(img.resize((w, h), _LANCZOS))

    return _cacheado(("rect", w, h, radio, relleno, borde, grosor, esquinas), crear)


def tarjeta(w, h, radio, relleno, borde, margen):
    """Fondo de tarjeta con borde fino y una sombra muy suave."""
    w, h = max(1, int(w)), max(1, int(h))

    def crear():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        # Sombra difuminada
        sombra = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle(
            (margen, margen + 2, w - margen - 1, h - margen + 1),
            radio, fill=(16, 24, 40, 20))
        sombra = sombra.filter(ImageFilter.GaussianBlur(max(1, margen - 1)))
        img.alpha_composite(sombra)
        # Tarjeta (supersampling para suavizar las esquinas)
        cw, ch = w - 2 * margen, h - 2 * margen
        if cw > 2 and ch > 2:
            ss = _ss(cw, ch)
            grande = Image.new("RGBA", (cw * ss, ch * ss), (0, 0, 0, 0))
            d = ImageDraw.Draw(grande)
            d.rounded_rectangle((0, 0, cw * ss - 1, ch * ss - 1), radio * ss, fill=_hex(borde))
            d.rounded_rectangle((ss, ss, cw * ss - 1 - ss, ch * ss - 1 - ss),
                                (radio - 1) * ss, fill=_hex(relleno))
            img.alpha_composite(grande.resize((cw, ch), _LANCZOS), (margen, margen))
        return ImageTk.PhotoImage(img)

    return _cacheado(("tarjeta", w, h, radio, relleno, borde, margen), crear)


def circulo(diametro, relleno, borde=None, grosor=0):
    def crear():
        ss = 4
        D = diametro * ss
        img = Image.new("RGBA", (D, D), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if borde:
            d.ellipse((0, 0, D - 1, D - 1), fill=_hex(borde))
            g = grosor * ss
            d.ellipse((g, g, D - 1 - g, D - 1 - g), fill=_hex(relleno))
        else:
            d.ellipse((0, 0, D - 1, D - 1), fill=_hex(relleno))
        return ImageTk.PhotoImage(img.resize((diametro, diametro), _LANCZOS))
    return _cacheado(("circulo", diametro, relleno, borde, grosor), crear)


def donut(tamaño, valores, colores, grosor, vacio="#eaecf0", hueco=2.5):
    """Gráfico de anillo. 'valores' y 'colores' son listas paralelas."""
    def crear():
        ss = 3
        S = tamaño * ss
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        total = sum(valores)
        caja = (0, 0, S - 1, S - 1)
        if total == 0:
            d.ellipse(caja, fill=_hex(vacio))
        else:
            activos = [(v, c) for v, c in zip(valores, colores) if v > 0]
            separacion = hueco if len(activos) > 1 else 0
            angulo = -90.0
            for valor, color in activos:
                barrido = 360.0 * valor / total
                d.pieslice(caja, angulo + separacion / 2,
                           angulo + barrido - separacion / 2, fill=_hex(color))
                angulo += barrido
        g = grosor * ss
        d.ellipse((g, g, S - 1 - g, S - 1 - g), fill=(0, 0, 0, 0))
        return ImageTk.PhotoImage(img.resize((tamaño, tamaño), _LANCZOS))
    return _cacheado(("donut", tamaño, tuple(valores), tuple(colores), grosor), crear)


# ---------------------------------------------------------------------------
# Iconos (dibujados en una cuadrícula de 24x24, estilo "línea")
# ---------------------------------------------------------------------------
def icono(nombre, tamaño, color, grosor=2.0):
    def crear():
        ss = 6
        S = tamaño * ss
        k = S / 24.0
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        c = _hex(color)
        g = max(1, round(grosor * k))

        def P(*pts):
            return [(x * k, y * k) for x, y in pts]

        def linea(*pts):
            pts = P(*pts)
            d.line(pts, fill=c, width=g, joint="curve")
            for x, y in (pts[0], pts[-1]):  # extremos redondeados
                d.ellipse((x - g / 2, y - g / 2, x + g / 2, y + g / 2), fill=c)

        def circ(cx, cy, r, relleno=False):
            caja = ((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k)
            if relleno:
                d.ellipse(caja, fill=c)
            else:
                d.ellipse(caja, outline=c, width=g)

        def arco(x0, y0, x1, y1, a0, a1):
            d.arc((x0 * k, y0 * k, x1 * k, y1 * k), a0, a1, fill=c, width=g)

        def caja(x0, y0, x1, y1, r):
            d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), r * k, outline=c, width=g)

        if nombre == "escritorio":
            caja(3, 3, 10.5, 10.5, 2); caja(13.5, 3, 21, 10.5, 2)
            caja(3, 13.5, 10.5, 21, 2); caja(13.5, 13.5, 21, 21, 2)
        elif nombre == "contactos":
            circ(9, 8, 4); arco(1.5, 14, 16.5, 30, 180, 360)
            arco(13, 4, 19, 12, 270, 90); arco(15, 14, 23, 30, 270, 360)
        elif nombre == "usuario":
            circ(12, 8, 4.5); arco(4, 15, 20, 31, 180, 360)
        elif nombre == "graficos":
            linea((6, 20), (6, 13)); linea((12, 20), (12, 5)); linea((18, 20), (18, 10))
        elif nombre == "info":
            circ(12, 12, 9.5); linea((12, 11), (12, 16.5)); circ(12, 7.6, 1.3, True)
        elif nombre == "buscar":
            circ(10.5, 10.5, 6.5); linea((15.5, 15.5), (20.5, 20.5))
        elif nombre == "mas":
            linea((12, 5), (12, 19)); linea((5, 12), (19, 12))
        elif nombre == "cerrar":
            linea((6, 6), (18, 18)); linea((18, 6), (6, 18))
        elif nombre == "check":
            linea((5, 12.5), (10, 17.5), (19, 7))
        elif nombre == "papelera":
            linea((4, 6.5), (20, 6.5)); linea((9, 6.5), (9, 3.5), (15, 3.5), (15, 6.5))
            linea((6, 6.5), (7, 20.5), (17, 20.5), (18, 6.5))
            linea((10, 10.5), (10, 16.5)); linea((14, 10.5), (14, 16.5))
        elif nombre == "telefono":
            caja(6.5, 2.5, 17.5, 21.5, 2.5); linea((11, 18), (13, 18))
        elif nombre == "email":
            caja(3, 5, 21, 19, 2.5); linea((3.5, 7), (12, 13), (20.5, 7))
        elif nombre == "etiqueta":
            d.polygon(P((3, 3), (11.5, 3), (21, 12.5), (12.5, 21), (3, 11.5)), outline=c, width=g)
            circ(7.8, 7.8, 1.4, True)
        elif nombre == "amigos":
            circ(12, 12, 9.5); arco(7, 7, 17, 17, 25, 155)
            circ(9, 9.8, 1.2, True); circ(15, 9.8, 1.2, True)
        elif nombre == "trabajo":
            caja(3, 7.5, 21, 20, 2.5); linea((9, 7.5), (9, 4), (15, 4), (15, 7.5))
            linea((3.5, 13), (20.5, 13))
        elif nombre == "familia":
            linea((3, 11), (12, 3.5), (21, 11))
            linea((5.5, 9.5), (5.5, 20.5), (18.5, 20.5), (18.5, 9.5))
            linea((10, 20.5), (10, 15), (14, 15), (14, 20.5))
        elif nombre == "externo":
            linea((14, 4), (20, 4), (20, 10)); linea((20, 4), (11, 13))
            linea((18, 14), (18, 20), (4, 20), (4, 6), (10, 6))
        elif nombre == "editar":
            linea((4, 20), (4.5, 16), (16, 4.5), (19.5, 8), (8, 19.5), (4, 20))
        elif nombre == "flecha":
            linea((5, 12), (19, 12)); linea((13, 6), (19, 12), (13, 18))

        return ImageTk.PhotoImage(img.resize((tamaño, tamaño), _LANCZOS))

    return _cacheado(("icono", nombre, tamaño, color, grosor), crear)
