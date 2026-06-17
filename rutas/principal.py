"""
Rutas de la pantalla de inicio: la página de inicio y el endpoint que le da
los datos a las gráficas (lo usa static/js/graficos.js con Chart.js).
"""

from flask import Blueprint, render_template, jsonify

from modelos.conexion import obtener_conexion
from modelos import incidencia

# El primer argumento es el nombre del blueprint (lo uso en url_for, p. ej.
# url_for('principal.inicio')).
bp_principal = Blueprint("principal", __name__)


@bp_principal.route("/")
def inicio():
    """Página de inicio: bienvenida, accesos rápidos y gráficas de resumen."""
    return render_template("inicio.html")


@bp_principal.route("/estadisticas")
def estadisticas():
    """
    Devuelve en JSON los datos para las gráficas (lo llama graficos.js). A cada
    gráfica le doy sus "labels" y sus "datos", que es lo que espera Chart.js.
    """
    con = obtener_conexion()
    try:
        por_estado = incidencia.contar_por_estado(con)
        por_mes    = incidencia.contar_por_mes(con)
    finally:
        con.close()

    # Fichas por estado: respeto el orden del ciclo y pongo 0 en los estados sin
    # fichas, para que la gráfica salga siempre con las cuatro porciones.
    datos_estado = [por_estado.get(e, 0) for e in incidencia.ESTADOS]

    # Fichas por mes: paso el mes de 'AAAA-MM' a 'MM/AAAA', que se lee mejor.
    etiquetas_mes = [f"{mes[5:7]}/{mes[0:4]}" for mes, _ in por_mes]
    datos_mes     = [total for _, total in por_mes]

    return jsonify({
        "por_estado": {"labels": list(incidencia.ESTADOS), "datos": datos_estado},
        "por_mes":    {"labels": etiquetas_mes,             "datos": datos_mes},
    })
