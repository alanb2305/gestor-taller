"""
Acceso a la tabla 'clientes'.

Cada función recibe la conexión ya abierta (con) y hace solo su consulta; el
commit y el cierre los hace la ruta, así varias altas pueden ir en la misma
transacción. Uso parámetros (?) en el SQL para evitar inyección SQL.
"""


def crear(con, datos: dict) -> int:
    """Inserta un cliente y devuelve su id. 'datos' tiene las claves de las columnas."""
    cursor = con.execute(
        """INSERT INTO clientes (nombre, cif, telefono, domicilio,
                                 numero, cp, poblacion)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datos.get("nombre", ""),
            datos.get("cif", ""),
            datos.get("telefono", ""),
            datos.get("domicilio", ""),
            datos.get("numero", ""),
            datos.get("cp", ""),
            datos.get("poblacion", ""),
        ),
    )
    return cursor.lastrowid


def actualizar(con, cliente_id: int, datos: dict) -> None:
    """
    Actualiza los datos de un cliente. Lo uso con el autorrelleno: si se reutiliza
    una matrícula y se corrige algún dato (teléfono, domicilio...), al guardar se
    queda lo último escrito. Mismas claves que en crear().
    """
    con.execute(
        """UPDATE clientes
              SET nombre    = ?,
                  cif       = ?,
                  telefono  = ?,
                  domicilio = ?,
                  numero    = ?,
                  cp        = ?,
                  poblacion = ?
            WHERE id = ?""",
        (
            datos.get("nombre", ""),
            datos.get("cif", ""),
            datos.get("telefono", ""),
            datos.get("domicilio", ""),
            datos.get("numero", ""),
            datos.get("cp", ""),
            datos.get("poblacion", ""),
            cliente_id,
        ),
    )


def obtener_por_id(con, cliente_id: int):
    """Devuelve la fila del cliente con ese id, o None si no existe."""
    return con.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,),
    ).fetchone()


def listar_todos(con) -> list:
    """Todos los clientes, ordenados por nombre. Lo usa la exportación a CSV."""
    return con.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()


def obtener_por_cif(con, cif: str):
    """Devuelve el cliente con ese CIF/DNI, o None. Lo usa la importación de CSV."""
    return con.execute(
        "SELECT * FROM clientes WHERE cif = ?", (cif,)
    ).fetchone()


def borrar(con, cliente_id: int) -> None:
    """Borra un cliente. Quien llama comprueba antes que no tenga vehículos."""
    con.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))


def listar_con_resumen(con) -> list:
    """
    Todos los clientes con cuántos vehículos tiene cada uno, para la pantalla de
    gestión. Uso LEFT JOIN para que los clientes sin coches salgan con 0.
    """
    return con.execute(
        """SELECT c.*, COUNT(v.id) AS n_vehiculos
             FROM clientes c
             LEFT JOIN vehiculos v ON v.cliente_id = c.id
            GROUP BY c.id
            ORDER BY c.nombre"""
    ).fetchall()
