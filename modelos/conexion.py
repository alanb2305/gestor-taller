"""
Conexión con la base de datos. Todo el acceso a SQLite pasa por aquí.
"""

import os
import sqlite3

from config import RUTA_BD, RUTA_ESQUEMA, DIR_FOTOS


def obtener_conexion():
    """Abre y devuelve una conexión a la base de datos."""
    conexion = sqlite3.connect(RUTA_BD)
    # Con row_factory = Row puedo leer las columnas por nombre (fila["nombre"]).
    conexion.row_factory = sqlite3.Row
    # SQLite trae las claves foráneas desactivadas; las activo.
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_bd():
    """
    Crea las carpetas y las tablas si no existen. Se llama al arrancar; como el
    esquema usa CREATE TABLE IF NOT EXISTS, si ya están creadas no pasa nada.
    """
    os.makedirs(os.path.dirname(RUTA_BD), exist_ok=True)
    os.makedirs(DIR_FOTOS, exist_ok=True)   # carpeta de las fotos de los daños

    with open(RUTA_ESQUEMA, encoding="utf-8") as fichero:
        sql = fichero.read()

    conexion = obtener_conexion()
    conexion.executescript(sql)   # ejecuta todas las sentencias del .sql
    conexion.commit()
    conexion.close()
