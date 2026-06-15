"""
Conexión con la base de datos.
Todo el acceso a SQLite pasa por aquí, así el resto de módulos
no tienen que preocuparse de cómo se abre la conexión.
"""

import os
import sqlite3

from config import RUTA_BD, RUTA_ESQUEMA


def obtener_conexion():
    """Abre y devuelve una conexión a la base de datos."""
    conexion = sqlite3.connect(RUTA_BD)
    # row_factory = Row nos deja leer las columnas por su nombre
    # (por ejemplo fila["nombre"]) en lugar de por posición.
    conexion.row_factory = sqlite3.Row
    # Activamos las claves foráneas (SQLite las trae desactivadas por defecto).
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_bd():
    """
    Crea la carpeta 'datos' y las tablas si todavía no existen.
    Se llama una vez al arrancar la app; si ya están creadas, no pasa nada
    porque el esquema usa CREATE TABLE IF NOT EXISTS.
    """
    os.makedirs(os.path.dirname(RUTA_BD), exist_ok=True)

    with open(RUTA_ESQUEMA, encoding="utf-8") as fichero:
        sql = fichero.read()

    conexion = obtener_conexion()
    conexion.executescript(sql)   # ejecuta todas las sentencias del .sql
    conexion.commit()
    conexion.close()
