#!/usr/bin/env python3
"""Agenda de Contactos — punto de entrada de la aplicación."""
import sys
from pathlib import Path

# Permite ejecutar la app desde cualquier carpeta
sys.path.insert(0, str(Path(__file__).resolve().parent))

from formularios.form_maestro_design import FormularioMaestroDesign  # noqa: E402

app = FormularioMaestroDesign()
app.mainloop()
