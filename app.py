"""
Punto de entrada de la app: crea la app de Flask, prepara la base de datos
y registra las rutas (que están repartidas en la carpeta 'rutas').
"""

import os

from flask import Flask

from config import NOMBRE_APP, CLAVE_SECRETA, TALLER, DIR_RECURSOS
from modelos.conexion import inicializar_bd
from servicios.formato import fecha_es
from rutas.principal import bp_principal
from rutas.incidencias import bp_incidencias
from rutas.agenda import bp_agenda
from rutas.datos import bp_datos
from rutas.clientes import bp_clientes
from rutas.vehiculos import bp_vehiculos

# Le digo a Flask dónde están las plantillas y los archivos estáticos a partir de
# DIR_RECURSOS. En ejecución normal es la carpeta del proyecto (lo de siempre);
# dentro del .exe es la carpeta temporal donde PyInstaller deja esos archivos, así
# que las plantillas se encuentran en los dos casos.
app = Flask(
    __name__,
    template_folder=os.path.join(DIR_RECURSOS, "templates"),
    static_folder=os.path.join(DIR_RECURSOS, "static"),
)

# Clave que usa Flask para los mensajes flash (y las sesiones).
app.secret_key = CLAVE_SECRETA

# Creamos la base de datos y las tablas si todavía no existen.
inicializar_bd()


# Con el context processor, los datos del taller están disponibles en todas
# las plantillas sin pasarlos en cada render_template (p. ej. {{ taller.nombre }}).
@app.context_processor
def inyectar_datos_comunes():
    return {"taller": TALLER, "app_nombre": NOMBRE_APP}


# Filtro para mostrar las fechas como dd/mm/aaaa en el HTML: {{ fecha | fecha_es }}
# (en la base de datos se guardan en formato ISO, AAAA-MM-DD).
app.add_template_filter(fecha_es, "fecha_es")


# Cada blueprint agrupa las rutas de una parte de la app.
app.register_blueprint(bp_principal)
app.register_blueprint(bp_incidencias)
app.register_blueprint(bp_agenda)
app.register_blueprint(bp_datos)
app.register_blueprint(bp_clientes)
app.register_blueprint(bp_vehiculos)


if __name__ == "__main__":
    # debug=True recarga el servidor al guardar cambios. Se quita al desplegar.
    app.run(debug=True)
