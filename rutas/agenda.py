"""
Agenda de entregas: una pantalla que reúne las fichas sin entregar que tienen
fecha de entrega y las reparte por urgencia (vencidas, hoy y próximas). No
necesita ninguna tabla nueva: los datos ya están en las incidencias.
"""

from datetime import date

from flask import Blueprint, render_template

from modelos.conexion import obtener_conexion
from modelos import incidencia

bp_agenda = Blueprint("agenda", __name__)


@bp_agenda.route("/agenda")
def agenda():
    """
    Lista las entregas pendientes en tres grupos según su fecha de entrega
    comparada con hoy: vencidas (antes de hoy), de hoy y próximas.
    """
    con = obtener_conexion()
    try:
        pendientes = incidencia.entregas_pendientes(con)
    finally:
        con.close()

    # Hoy en ISO (AAAA-MM-DD). Las fechas de la BD van en ese formato, así que
    # las comparo como texto (en ISO el orden alfabético es el cronológico).
    hoy = date.today().isoformat()

    vencidas = []
    de_hoy   = []
    proximas = []
    for ficha in pendientes:
        if ficha["fecha_entrega"] < hoy:
            vencidas.append(ficha)
        elif ficha["fecha_entrega"] == hoy:
            de_hoy.append(ficha)
        else:
            proximas.append(ficha)

    return render_template("agenda.html",
                           vencidas=vencidas, de_hoy=de_hoy, proximas=proximas)
