"""
Rutas de la pantalla de inicio.

Un 'blueprint' es simplemente un grupo de rutas que vive en su propio
fichero y que luego registramos en app.py. Sirve para tener el código
ordenado por zonas en vez de amontonar todas las rutas en un solo sitio.
"""

from flask import Blueprint, render_template

# 1er argumento: nombre interno del blueprint (lo usamos en url_for,
# p. ej. url_for('principal.inicio')). 2º (__name__): le dice a Flask
# dónde está este módulo para encontrar plantillas y estáticos.
bp_principal = Blueprint("principal", __name__)


@bp_principal.route("/")
def inicio():
    """Página de inicio: bienvenida y accesos rápidos."""
    return render_template("inicio.html")
