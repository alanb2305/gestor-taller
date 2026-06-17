"""
Funciones de formato compartidas. De momento solo está la de las fechas, que
usan el filtro de plantilla (app.py) y el PDF (servicios/pdf.py).
"""

from datetime import date


def fecha_es(iso):
    """
    Pasa una fecha de AAAA-MM-DD a dd/mm/aaaa. Si no es válida (None o texto
    raro), devuelve el valor tal cual para no romper la plantilla ni el PDF.
    """
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return iso or ""
