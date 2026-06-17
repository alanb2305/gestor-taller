"""
Acceso a la tabla 'vehiculos'.

Un vehículo pertenece siempre a un cliente (cliente_id) y se identifica
por la matrícula, que es UNIQUE en la tabla (no puede repetirse).
"""


def crear(con, matricula: str, marca_modelo: str, cliente_id: int) -> int:
    """Inserta un vehículo y devuelve su id."""
    cursor = con.execute(
        """INSERT INTO vehiculos (matricula, marca_modelo, cliente_id)
           VALUES (?, ?, ?)""",
        (matricula, marca_modelo, cliente_id),
    )
    return cursor.lastrowid


def actualizar_marca_modelo(con, vehiculo_id: int, marca_modelo: str) -> None:
    """
    Corrige la marca y el modelo de un vehículo. La matrícula no se toca (es lo
    que identifica al coche), pero la marca/modelo sí se pueden poner al día.
    """
    con.execute(
        "UPDATE vehiculos SET marca_modelo = ? WHERE id = ?",
        (marca_modelo, vehiculo_id),
    )


def obtener_por_matricula(con, matricula: str):
    """Devuelve el vehículo con esa matrícula, o None si no existe."""
    return con.execute(
        "SELECT * FROM vehiculos WHERE matricula = ?",
        (matricula,),
    ).fetchone()


def datos_para_autorrelleno(con, matricula: str):
    """
    Para el autorrelleno: a partir de una matrícula ya registrada, devuelve en
    una sola consulta (JOIN) los datos del vehículo y de su cliente. None si la
    matrícula es nueva.
    """
    return con.execute(
        """SELECT v.id            AS vehiculo_id,
                  v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  c.id            AS cliente_id,
                  c.nombre        AS nombre,
                  c.cif           AS cif,
                  c.telefono      AS telefono,
                  c.domicilio     AS domicilio,
                  c.numero        AS numero,
                  c.cp            AS cp,
                  c.poblacion     AS poblacion
             FROM vehiculos v
             JOIN clientes  c ON c.id = v.cliente_id
            WHERE v.matricula = ?""",
        (matricula,),
    ).fetchone()


def listar_todos_con_cliente(con) -> list:
    """
    Todos los vehículos con el CIF de su dueño, para exportar a CSV. Uso el CIF
    (no el id interno, que cambia entre bases de datos) para volver a enlazar
    cada coche con su cliente al importar.
    """
    return con.execute(
        """SELECT v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  c.cif           AS cif_cliente
             FROM vehiculos v
             JOIN clientes  c ON c.id = v.cliente_id
            ORDER BY v.matricula"""
    ).fetchall()


def obtener_por_id(con, vehiculo_id: int):
    """Devuelve el vehículo con ese id, o None. Lo usa la edición."""
    return con.execute(
        "SELECT * FROM vehiculos WHERE id = ?", (vehiculo_id,)
    ).fetchone()


def actualizar(con, vehiculo_id: int, marca_modelo: str, cliente_id: int) -> None:
    """
    Actualiza la marca/modelo y el dueño de un vehículo. La matrícula NO se
    cambia: es lo que identifica al coche.
    """
    con.execute(
        "UPDATE vehiculos SET marca_modelo = ?, cliente_id = ? WHERE id = ?",
        (marca_modelo, cliente_id, vehiculo_id),
    )


def borrar(con, vehiculo_id: int) -> None:
    """Borra un vehículo. Quien llama comprueba antes que no tenga fichas."""
    con.execute("DELETE FROM vehiculos WHERE id = ?", (vehiculo_id,))


def contar_por_cliente(con, cliente_id: int) -> int:
    """Cuántos vehículos tiene un cliente. Sirve para no borrar clientes con coches."""
    return con.execute(
        "SELECT COUNT(*) FROM vehiculos WHERE cliente_id = ?", (cliente_id,)
    ).fetchone()[0]


def listar_con_resumen(con) -> list:
    """
    Todos los vehículos con su dueño y cuántas fichas tienen, para la pantalla
    de gestión. LEFT JOIN con incidencias para contar 0 en los que no tienen.
    """
    return con.execute(
        """SELECT v.id            AS id,
                  v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  v.cliente_id    AS cliente_id,
                  c.nombre        AS cliente_nombre,
                  COUNT(i.id)     AS n_fichas
             FROM vehiculos   v
             JOIN clientes    c ON c.id = v.cliente_id
             LEFT JOIN incidencias i ON i.vehiculo_id = v.id
            GROUP BY v.id
            ORDER BY v.matricula"""
    ).fetchall()
