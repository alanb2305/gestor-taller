"""
Rutas de la pantalla de inicio.

Un 'blueprint' es simplemente un grupo de rutas que vive en su propio
fichero y que luego registramos en app.py. Sirve para tener el código
ordenado por zonas en vez de amontonar todas las rutas en un solo sitio.

Aquí están la página de inicio y el endpoint que le da los datos a las
gráficas (lo consume static/js/graficos.js con Chart.js).
"""

from flask import Blueprint, render_template, jsonify

from modelos.conexion import obtener_conexion
from modelos import incidencia

# 1er argumento: nombre interno del blueprint (lo usamos en url_for,
# p. ej. url_for('principal.inicio')). 2º (__name__): le dice a Flask
# dónde está este módulo para encontrar plantillas y estáticos.
bp_principal = Blueprint("principal", __name__)


@bp_principal.route("/")
def inicio():
    """Página de inicio: bienvenida, accesos rápidos y gráficas de resumen."""
    return render_template("inicio.html")


@bp_principal.route("/estadisticas")
def estadisticas():
    """
    Devuelve en JSON los datos para las gráficas de la pantalla de inicio.
    Lo llama static/js/graficos.js, que las dibuja con Chart.js.

    A cada gráfica le damos sus "labels" (las etiquetas que se ven) y sus
    "datos" (los números), que es justo lo que Chart.js espera recibir.
    """
    con = obtener_conexion()
    por_estado = incidencia.contar_por_estado(con)
    por_mes    = incidencia.contar_por_mes(con)
    top        = incidencia.clientes_con_mas_visitas(con, limite=5)
    con.close()

    # Fichas por estado: respetamos el orden natural del ciclo y ponemos 0 en
    # los estados que aún no tienen ninguna ficha, para que la gráfica salga
    # siempre con las mismas cuatro porciones.
    datos_estado = [por_estado.get(e, 0) for e in incidencia.ESTADOS]

    # Fichas por mes: pasamos el mes de 'AAAA-MM' a 'MM/AAAA', que se lee mejor.
    etiquetas_mes = [f"{mes[5:7]}/{mes[0:4]}" for mes, _ in por_mes]
    datos_mes     = [total for _, total in por_mes]

    # Clientes que más vuelven.
    etiquetas_top = [nombre for nombre, _ in top]
    datos_top     = [total for _, total in top]

    return jsonify({
        "por_estado": {"labels": list(incidencia.ESTADOS), "datos": datos_estado},
        "por_mes":    {"labels": etiquetas_mes,             "datos": datos_mes},
        "clientes":   {"labels": etiquetas_top,             "datos": datos_top},
    })
