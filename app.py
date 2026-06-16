"""
Punto de entrada de la aplicación.
Crea la app de Flask, deja preparada la base de datos y registra las rutas,
que tenemos repartidas en la carpeta 'rutas' para no juntarlo todo aquí.
"""

from datetime import date

from flask import Flask

from config import NOMBRE_APP, CLAVE_SECRETA, TALLER
from modelos.conexion import inicializar_bd
from rutas.principal import bp_principal
from rutas.incidencias import bp_incidencias

app = Flask(__name__)

# Clave para los mensajes flash y, más adelante, para las sesiones.
app.secret_key = CLAVE_SECRETA

# Al arrancar dejamos creado el fichero de la base de datos y las tablas
# si aún no existen. El acceso a datos (dar de alta, consultar...) lo
# desarrollamos en el siguiente bloque; de momento solo lo dejamos listo.
inicializar_bd()


# ---------------------------------------------------------------------------
# Context processor: una función que mete variables en TODAS las plantillas
# sin tener que pasarlas a mano en cada render_template(). Así, en cualquier
# HTML podemos usar {{ taller.nombre }} o {{ app_nombre }}.
# Lo usamos para que la cabecera y el resguardo cojan los datos del taller
# desde config.py: la app es genérica y su identidad vive solo en config.
# ---------------------------------------------------------------------------
@app.context_processor
def inyectar_datos_comunes():
    return {"taller": TALLER, "app_nombre": NOMBRE_APP}


# ---------------------------------------------------------------------------
# Filtro de plantilla para mostrar las fechas.
# En la base de datos y en los <input type="date"> las fechas van en formato
# ISO (AAAA-MM-DD), pero en el resguardo queremos verlas a la española
# (dd/mm/aaaa). Con este filtro, en el HTML basta escribir:  {{ fecha | fecha_es }}
# ---------------------------------------------------------------------------
@app.template_filter("fecha_es")
def fecha_es(iso):
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return iso or ""


# Registramos los blueprints: cada uno agrupa las rutas de una parte de la
# app. Hoy tenemos la pantalla de inicio y la de incidencias; al crecer el
# proyecto añadiremos las de clientes, vehículos, etc.
app.register_blueprint(bp_principal)
app.register_blueprint(bp_incidencias)


if __name__ == "__main__":
    # debug=True recarga el servidor al guardar cambios. Se quita al desplegar.
    app.run(debug=True)
