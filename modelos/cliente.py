"""
Acceso a la tabla 'clientes'.

Cada función recibe una conexión ya abierta (con) y se ocupa solo de su
consulta. No abre, no cierra y no hace commit: de eso se encarga quien
llama (normalmente una ruta), así podemos agrupar varias altas en una
misma transacción.

Todas las consultas usan parámetros (?) en lugar de pegar el texto en el
SQL, para evitar inyección SQL.
"""


def crear(con, datos: dict) -> int:
    """
    Inserta un cliente y devuelve su id (el AUTOINCREMENT de SQLite).
    'datos' es un diccionario con las claves de las columnas.
    """
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
    Actualiza los datos de un cliente que ya existe.

    Lo usamos junto con el autorrelleno: cuando se teclea una matrícula ya
    registrada, el formulario trae los datos guardados; si el usuario los
    corrige (un teléfono nuevo, un cambio de domicilio...) y guarda, aquí
    dejamos en la base de datos lo último que se ha escrito.

    Se actualizan las mismas columnas que se rellenan en el formulario.
    Las claves del diccionario son las mismas que en crear().
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


def buscar_por_nombre(con, texto: str) -> list:
    """
    Clientes cuyo nombre contenga 'texto'. Lo usa el buscador del
    historial. SQLite no distingue mayúsculas en LIKE para letras
    normales (sí en las acentuadas; eso queda como mejora futura).
    """
    patron = f"%{texto}%"
    return con.execute(
        "SELECT * FROM clientes WHERE nombre LIKE ? ORDER BY nombre",
        (patron,),
    ).fetchall()


def listar_todos(con) -> list:
    """Todos los clientes, ordenados por nombre. Lo usa la exportación a CSV."""
    return con.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()


def obtener_por_cif(con, cif: str):
    """
    Devuelve el cliente con ese CIF/DNI, o None. Lo usa la importación para
    saber si un cliente ya existe (y entonces actualizarlo en vez de duplicarlo).
    """
    return con.execute(
        "SELECT * FROM clientes WHERE cif = ?", (cif,)
    ).fetchone()


def borrar(con, cliente_id: int) -> None:
    """Borra un cliente. Quien llama comprueba antes que no tenga vehículos."""
    con.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))


def listar_con_resumen(con) -> list:
    """
    Todos los clientes con cuántos vehículos tiene cada uno, para la pantalla
    de gestión. El LEFT JOIN hace que los clientes sin coches salgan con 0
    (con un JOIN normal no aparecerían).
    """
    return con.execute(
        """SELECT c.*, COUNT(v.id) AS n_vehiculos
             FROM clientes c
             LEFT JOIN vehiculos v ON v.cliente_id = c.id
            GROUP BY c.id
            ORDER BY c.nombre"""
    ).fetchall()
