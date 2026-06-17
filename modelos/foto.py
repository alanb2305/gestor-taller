"""
Acceso a la tabla 'fotos'.

Cada foto pertenece a una incidencia (incidencia_id) y guarda solo el nombre
del archivo; la imagen en sí vive en DIR_FOTOS, fuera de la base de datos. Así
la base de datos no engorda con los binarios y las fotos se sirven como
ficheros normales. Mismo patrón que el resto de modelos: las funciones reciben
la conexión ya abierta y no hacen commit ni la cierran (de eso se encarga la
ruta).
"""


def crear(con, incidencia_id: int, nombre_archivo: str) -> int:
    """Inserta una foto (su nombre de archivo) para una incidencia."""
    cursor = con.execute(
        """INSERT INTO fotos (incidencia_id, nombre_archivo)
           VALUES (?, ?)""",
        (incidencia_id, nombre_archivo),
    )
    return cursor.lastrowid


def listar_por_incidencia(con, incidencia_id: int) -> list:
    """Todas las fotos de una incidencia, en el orden en que se subieron."""
    return con.execute(
        """SELECT * FROM fotos
            WHERE incidencia_id = ?
            ORDER BY id""",
        (incidencia_id,),
    ).fetchall()


def obtener_por_id(con, foto_id: int):
    """
    Devuelve la foto con ese id, o None si no existe.
    La usan el borrado y la ruta que sirve la imagen, que además comprueban
    que la foto sea de la incidencia indicada en la URL.
    """
    return con.execute(
        "SELECT * FROM fotos WHERE id = ?", (foto_id,)
    ).fetchone()


def borrar(con, foto_id: int) -> None:
    """Borra la fila de una foto. El archivo lo borra aparte servicios/fotos.py."""
    con.execute("DELETE FROM fotos WHERE id = ?", (foto_id,))
