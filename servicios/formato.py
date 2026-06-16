"""
Pequeñas funciones de formato compartidas.

Reúnen en un solo sitio el formateo que se usa en más de un lado, para no
repetir la misma lógica. De momento solo está el de las fechas: pasarlas de
ISO (AAAA-MM-DD) al formato español (dd/mm/aaaa). Lo usan el filtro de
plantilla (app.py) y la generación del PDF (servicios/pdf.py); antes estaba
escrito igual en los dos sitios.
"""

from datetime import date


def fecha_es(iso):
    """
    Pasa una fecha AAAA-MM-DD a dd/mm/aaaa.
    Si no es una fecha válida (None o un texto raro), devuelve el valor tal
    cual (o cadena vacía), para no romper la plantilla ni el PDF.
    """
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return iso or ""
