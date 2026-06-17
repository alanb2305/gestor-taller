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


def obtener_estado(con, incidencia_id: int):
    """
    Devuelve solo el estado de una incidencia, o None si no existe.
    Lo usa avanzar_estado: para calcular el siguiente estado no hacen falta los
    datos del cliente ni del vehículo, solo saber en qué estado está, así que
    nos ahorramos los JOIN de obtener_completa().
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
    Entregas que aún están pendientes, para la agenda.

    Trae las fichas que NO se han entregado y que tienen fecha de entrega,
    junto con su vehículo y su cliente (mismo JOIN que listar()). Dejamos fuera
    a propósito dos casos: las ya 'entregado' (no hay nada que agendar) y las
    que no tienen fecha_entrega (no se pueden situar en la agenda).

    Ordenamos por fecha_entrega: como se guarda en ISO (AAAA-MM-DD), ordenar el
    texto ordena igual que por fecha (de la más urgente a la más lejana).
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
    Devuelve el estado que va justo después del actual en el ciclo de trabajo
    (recepcionado -> en reparación -> terminado -> entregado), o None si la
    ficha ya está en el último estado ('entregado').

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


# ---------------------------------------------------------------------------
# Consultas para las gráficas de la pantalla de inicio.
# Son agregaciones (COUNT ... GROUP BY): no devuelven fichas sueltas, sino
# recuentos. Devuelven estructuras de Python normales (diccionario o lista de
# tuplas); el JSON que necesita Chart.js lo arma la ruta.
# ---------------------------------------------------------------------------

def contar_por_estado(con) -> dict:
    """
    Cuenta cuántas fichas hay en cada estado.
    Devuelve un diccionario {estado: nº de fichas} solo con los estados que
    tienen alguna ficha (la ruta ya completa con 0 los que falten).
    """
    filas = con.execute(
        "SELECT estado, COUNT(*) AS total FROM incidencias GROUP BY estado"
    ).fetchall()
    return {fila["estado"]: fila["total"] for fila in filas}


def contar_por_mes(con) -> list:
    """
    Cuenta las fichas por mes de entrada.
    Devuelve una lista de tuplas (mes, total) ordenada de más antiguo a más
    reciente, con el mes en formato 'AAAA-MM'. Como la fecha se guarda como
    'AAAA-MM-DD', nos quedamos con los 7 primeros caracteres (substr).
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
    Todas las fichas con TODOS sus datos (vehículo, cliente y las reparaciones
    juntas en una sola celda separadas por '|'), para exportar el historial a
    CSV. group_concat es de SQLite: junta en un solo texto las varias
    reparaciones de una misma ficha.
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
