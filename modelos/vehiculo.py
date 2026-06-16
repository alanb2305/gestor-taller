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
    Corrige la marca y el modelo de un vehículo ya registrado.

    La matrícula NO se cambia: es lo que identifica al coche. Pero la marca
    o el modelo sí pueden haberse escrito mal la primera vez, así que cuando
    se reutiliza una matrícula con el autorrelleno dejamos guardado lo que
    aparezca escrito al guardar.
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
    Para el autorrelleno del formulario: a partir de una matrícula que ya
    está registrada, devuelve en UNA sola consulta los datos del vehículo
    y los de su cliente, juntando las dos tablas con un JOIN.
    Devuelve None si la matrícula es nueva (todavía no existe).
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
    Todos los vehículos junto con el CIF de su dueño, para la exportación a CSV.
    Usamos el CIF (no el id interno, que cambia de una base de datos a otra)
    como forma de volver a enlazar cada coche con su cliente al importar.
    """
    return con.execute(
        """SELECT v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  c.cif           AS cif_cliente
             FROM vehiculos v
             JOIN clientes  c ON c.id = v.cliente_id
            ORDER BY v.matricula"""
    ).fetchall()
