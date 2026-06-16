"""
Acceso a la tabla 'incidencias' (las órdenes de trabajo).

Una incidencia es una entrada del coche al taller. Enlaza con un
vehículo (vehiculo_id) y va pasando por varios estados durante la
reparación.

Las fechas se guardan como AAAA-MM-DD, que es el formato de SQLite y también
el que devuelve el <input type="date"> del formulario, así que se guardan tal
cual. Para mostrarlas a la española (dd/mm/aaaa) está el filtro fecha_es de la
plantilla; aquí no convertimos nada.
"""

# Estados válidos, en el orden natural del trabajo. Es el mismo CHECK que
# hay en el esquema; lo repetimos aquí para validar antes de tocar la base
# de datos y poder dar un mensaje claro.
ESTADOS = ("recibido", "en reparación", "terminado", "entregado")


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
            datos.get("estado", "recibido"),
            datos.get("recoger_piezas", "No"),
        ),
    )
    return cursor.lastrowid


def obtener_completa(con, incidencia_id: int):
    """
    Devuelve, en una sola fila, todos los datos de una incidencia junto
    con los de su vehículo y su cliente (dos JOIN encadenados). Es lo que
    necesita el resguardo para volver a imprimirse desde el historial.
    Las líneas de reparación se piden aparte con
    reparacion.listar_por_incidencia().
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


def buscar(con, texto: str) -> list:
    """Busca incidencias por matrícula, nombre del cliente o fecha de entrada."""
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
            ORDER BY i.id DESC""",
        (patron, patron, patron),
    ).fetchall()


def siguiente_estado(estado_actual: str):
    """
    Devuelve el estado que va justo después del actual en el ciclo de trabajo
    (recibido -> en reparación -> terminado -> entregado), o None si la ficha
    ya está en el último estado ('entregado').

    Lo usa el botón de "avanzar estado" del historial: el orden es el de la
    tupla ESTADOS, así que el siguiente es simplemente el de la posición + 1.
    """
    try:
        posicion = ESTADOS.index(estado_actual)
    except ValueError:
        # Estado desconocido (no debería pasar: la columna tiene un CHECK en
        # el esquema). Por si acaso, no proponemos ningún avance.
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
