"""
Acceso a la tabla 'reparaciones'.

Cada incidencia tiene una o varias líneas de reparación, cada una como una
fila. (En el programa original eran 5 líneas fijas; aquí van las que hagan falta.)
"""


def crear(con, incidencia_id: int, descripcion: str) -> int:
    """Inserta una línea de reparación para una incidencia."""
    cursor = con.execute(
        """INSERT INTO reparaciones (incidencia_id, descripcion)
           VALUES (?, ?)""",
        (incidencia_id, descripcion),
    )
    return cursor.lastrowid


def crear_varias(con, incidencia_id: int, descripciones) -> None:
    """
    Inserta varias líneas de golpe (las que vienen del formulario).
    Se saltan las vacías para no guardar líneas en blanco.
    """
    for texto in descripciones:
        texto = (texto or "").strip()
        if texto:
            crear(con, incidencia_id, texto)


def listar_por_incidencia(con, incidencia_id: int) -> list:
    """Todas las líneas de una incidencia, en el orden en que se metieron."""
    return con.execute(
        """SELECT * FROM reparaciones
            WHERE incidencia_id = ?
            ORDER BY id""",
        (incidencia_id,),
    ).fetchall()
