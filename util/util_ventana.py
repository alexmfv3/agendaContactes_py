def centrarVentana(ventana, aplicacionAncho, aplicacionLargo):
    """Coloca la ventana en el centro de la pantalla."""
    pantallaAncho = ventana.winfo_screenwidth()
    pantallaLargo = ventana.winfo_screenheight()
    x = max(0, int((pantallaAncho / 2) - (aplicacionAncho / 2)))
    y = max(0, int((pantallaLargo / 2) - (aplicacionLargo / 2)) - 20)
    return ventana.geometry(f"{aplicacionAncho}x{aplicacionLargo}+{x}+{y}")


def centrarSobre(ventana, padre, ancho, alto):
    """Coloca una ventana secundaria en el centro de su ventana padre."""
    padre.update_idletasks()
    x = padre.winfo_rootx() + (padre.winfo_width() - ancho) // 2
    y = padre.winfo_rooty() + (padre.winfo_height() - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{max(0, x)}+{max(0, y)}")
