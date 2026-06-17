"""
Acceso a la tabla 'incidencias' (las órdenes de trabajo).

Una incidencia es una entrada del coche al taller: enlaza con un vehículo y va
pasando por varios estados. Las fechas se guardan en formato ISO (AAAA-MM-DD),
que es el que usan SQLite y el <input type="date">, así que se guardan tal cual.
"""

# Estados válidos, en el orden del trabajo. Es el mismo CHECK del esquema; lo
# repito aquí para validar antes de tocar la base de datos.
ESTADOS = ("recepcionado", "en reparación", "terminado", "entregado")


def crear(con, datos: dict) -> int:
    """Inserta una incidencia y devuelve su id."""
    cursor = con.execute(
        """INSERT INTO incidencias (vehiculo_id, fecha_entrada, fecha_entrega,
                                    kilometros, combustible, estado,
                                    recoger_piezas)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datos["vehiculo_id"],
            datos["fecha_entrada"],
            datos.get("fecha_entrega"),
            datos.get("kilometros"),
            datos.get("combustible"),
            datos.get("estado", "recepcionado"),
            datos.get("recoger_piezas", "No"),
        ),
    )
    return cursor.lastrowid


def obtener_completa(con, incidencia_id: int):
    """
    Devuelve en una sola fila los datos de la incidencia con los de su vehículo
    y su cliente (dos JOIN), que es lo que necesita el resguardo. Las líneas de
    reparación se piden aparte con reparacion.listar_por_incidencia().
    """
    return con.execute(
        """SELECT i.*,
                  v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  c.nombre        AS nombre,
                  c.cif           AS cif,
                  c.telefono      AS telefono,
                  c.domicilio     AS domicilio,
                  c.numero        AS numero,
                  c.cp            AS cp,
                  c.poblacion     AS poblacion
             FROM incidencias i
             JOIN vehiculos    v ON v.id = i.vehiculo_id
             JOIN clientes     c ON c.id = v.cliente_id
            WHERE i.id = ?""",
        (incidencia_id,),
    ).fetchone()


def obtener_estado(con, incidencia_id: int):
    """
    Devuelve solo el estado de una incidencia, o None si no existe. Para avanzar
    de estado no hacen falta los JOIN de obtener_completa(), solo el estado.
    """
    fila = con.execute(
        "SELECT estado FROM incidencias WHERE id = ?",
        (incidencia_id,),
    ).fetchone()
    return fila["estado"] if fila else None


def listar(con, limite: int = 50) -> list:
    """Últimas incidencias (las más recientes primero) para el historial."""
    return con.execute(
        """SELECT i.id            AS id,
                  i.fecha_entrada AS fecha_entrada,
                  i.fecha_entrega AS fecha_entrega,
                  i.estado        AS estado,
                  v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  c.nombre        AS nombre
             FROM incidencias i
             JOIN vehiculos    v ON v.id = i.vehiculo_id
             JOIN clientes     c ON c.id = v.cliente_id
            ORDER BY i.id DESC
            LIMIT ?""",
        (limite,),
    ).fetchall()


def buscar(con, texto: str, limite: int = 50) -> list:
    """
    Busca incidencias por matrícula, nombre del cliente o fecha de entrada.
    Lleva LIMIT, igual que listar(), para no traer un historial enorme de
    golpe si la búsqueda coincide con muchas fichas.
    """
    patron = f"%{texto}%"
    return con.execute(
        """SELECT i.id            AS id,
                  i.fecha_entrada AS fecha_entrada,
                  i.fecha_entrega AS fecha_entrega,
                  i.estado        AS estado,
                  v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  c.nombre        AS nombre
             FROM incidencias i
             JOIN vehiculos    v ON v.id = i.vehiculo_id
             JOIN clientes     c ON c.id = v.cliente_id
            WHERE v.matricula     LIKE ?
               OR c.nombre        LIKE ?
               OR i.fecha_entrada LIKE ?
            ORDER BY i.id DESC
            LIMIT ?""",
        (patron, patron, patron, limite),
    ).fetchall()


def entregas_pendientes(con) -> list:
    """
    Fichas pendientes de entregar para la agenda: las que NO están 'entregado' y
    tienen fecha de entrega. Se ordenan por fecha_entrega (en ISO, así el orden
    del texto coincide con el cronológico: de la más urgente a la más lejana).
    """
    return con.execute(
        """SELECT i.id            AS id,
                  i.fecha_entrada AS fecha_entrada,
                  i.fecha_entrega AS fecha_entrega,
                  i.estado        AS estado,
                  v.matricula     AS matricula,
                  v.marca_modelo  AS marca_modelo,
                  c.nombre        AS nombre
             FROM incidencias i
             JOIN vehiculos    v ON v.id = i.vehiculo_id
             JOIN clientes     c ON c.id = v.cliente_id
            WHERE i.estado != 'entregado'
              AND i.fecha_entrega IS NOT NULL
            ORDER BY i.fecha_entrega"""
    ).fetchall()


def siguiente_estado(estado_actual: str):
    """
    Devuelve el estado siguiente al actual (recepcionado -> en reparación ->
    terminado -> entregado), o None si ya está en el último. Como el orden es el
    de la tupla ESTADOS, el siguiente es el de la posición + 1.
    """
    try:
        posicion = ESTADOS.index(estado_actual)
    except ValueError:
        # Estado desconocido (no debería pasar por el CHECK del esquema).
        return None
    if posicion + 1 < len(ESTADOS):
        return ESTADOS[posicion + 1]
    return None


def cambiar_estado(con, incidencia_id: int, nuevo_estado: str) -> None:
    if nuevo_estado not in ESTADOS:
        raise ValueError(f"Estado no válido: {nuevo_estado!r}")
    con.execute(
        "UPDATE incidencias SET estado = ? WHERE id = ?",
        (nuevo_estado, incidencia_id),
    )


# ---------------------------------------------------------------------------
# Consultas para las gráficas de la pantalla de inicio (COUNT ... GROUP BY).
# Devuelven recuentos; el JSON que necesita Chart.js lo arma la ruta.
# ---------------------------------------------------------------------------

def contar_por_estado(con) -> dict:
    """
    Cuenta las fichas que hay en cada estado. Devuelve {estado: nº de fichas}
    solo con los estados que tienen alguna (la ruta completa con 0 los demás).
    """
    filas = con.execute(
        "SELECT estado, COUNT(*) AS total FROM incidencias GROUP BY estado"
    ).fetchall()
    return {fila["estado"]: fila["total"] for fila in filas}


def contar_por_mes(con) -> list:
    """
    Cuenta las fichas por mes de entrada. Devuelve una lista de tuplas
    (mes, total) con el mes en 'AAAA-MM' (los 7 primeros caracteres de la fecha).
    """
    filas = con.execute(
        """SELECT substr(fecha_entrada, 1, 7) AS mes, COUNT(*) AS total
             FROM incidencias
            GROUP BY mes
            ORDER BY mes"""
    ).fetchall()
    return [(fila["mes"], fila["total"]) for fila in filas]


def contar_por_vehiculo(con, vehiculo_id: int) -> int:
    """Cuántas fichas tiene un vehículo. Sirve para no borrar coches con historial."""
    return con.execute(
        "SELECT COUNT(*) FROM incidencias WHERE vehiculo_id = ?", (vehiculo_id,)
    ).fetchone()[0]


def listar_completo(con) -> list:
    """
    Todas las fichas con todos sus datos (vehículo, cliente y las reparaciones
    en una sola celda separadas por '|'), para exportar el historial a CSV.
    group_concat (de SQLite) junta en un texto las reparaciones de cada ficha.
    """
    return con.execute(
        """SELECT i.id             AS numero_ficha,
                  i.fecha_entrada  AS fecha_entrada,
                  i.fecha_entrega  AS fecha_entrega,
                  i.estado         AS estado,
                  v.matricula      AS matricula,
                  v.marca_modelo   AS marca_modelo,
                  i.kilometros     AS kilometros,
                  i.combustible    AS combustible,
                  i.recoger_piezas AS recoger_piezas,
                  c.nombre         AS nombre,
                  c.cif            AS cif,
                  c.telefono       AS telefono,
                  c.domicilio      AS domicilio,
                  c.numero         AS numero,
                  c.cp             AS cp,
                  c.poblacion      AS poblacion,
                  (SELECT group_concat(r.descripcion, '|')
                     FROM reparaciones r
                    WHERE r.incidencia_id = i.id) AS reparaciones
             FROM incidencias i
             JOIN vehiculos    v ON v.id = i.vehiculo_id
             JOIN clientes     c ON c.id = v.cliente_id
            ORDER BY i.id"""
    ).fetchall()
