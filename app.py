"""
Punto de entrada de la aplicación.
De momento solo arranca Flask y se asegura de que la base de datos existe.
A partir de aquí iremos añadiendo las pantallas (las rutas).
"""

from flask import Flask

from config import NOMBRE_APP
from modelos.conexion import inicializar_bd

app = Flask(__name__)

# Al arrancar, creamos la base de datos y las tablas si aún no existen.
inicializar_bd()


@app.route("/")
def inicio():
    return f"{NOMBRE_APP} · la base de datos está lista ✅"


if __name__ == "__main__":
    # debug=True recarga el servidor al guardar cambios. Se quita al desplegar.
    app.run(debug=True)
