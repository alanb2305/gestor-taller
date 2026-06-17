"""
Agenda de entregas.

Una pantalla sencilla que reúne las fichas que aún no se han entregado y que
tienen fecha de entrega, repartidas por urgencia (vencidas, hoy y próximas).
No hace falta ninguna tabla nueva: los datos ya están en las incidencias
(fecha_entrega y estado); aquí solo los consultamos y los agrupamos. La idea es
tener a la vista qué coches toca entregar, sin montar un calendario interactivo.
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

    # Hoy en ISO (AAAA-MM-DD). Las fechas de la base de datos van en ese mismo
    # formato, así que las comparamos como texto: en ISO el orden alfabético
    # coincide con el cronológico (el mismo truco que usa validaciones.js).
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
