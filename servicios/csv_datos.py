"""
Importar y exportar datos en CSV (clientes, vehículos e historial), para usarlos
en Excel. Uso el módulo 'csv' de Python, nada externo.

Para que los CSV se abran bien en el Excel español uso separador ';' y
codificación UTF-8 con BOM ('utf-8-sig'), así los acentos y la Ñ salen bien.

Al importar reaprovecho las validaciones del formulario, así una fila importada
pasa los mismos controles que una ficha escrita a mano. Las funciones de
importar NO hacen commit: de la transacción se encarga la ruta.
"""

import csv
import io

from servicios import validaciones
from modelos import cliente, vehiculo, incidencia, reparacion


_SEP = ";"
_CODIFICACION = "utf-8-sig"

# Cabeceras de cada CSV. Marcan el orden de las columnas al exportar y las
# columnas que esperamos encontrar al importar.
CABECERAS_CLIENTES  = ["nombre", "cif", "telefono", "domicilio",
                       "numero", "cp", "poblacion"]
CABECERAS_VEHICULOS = ["matricula", "marca_modelo", "cif_cliente"]
CABECERAS_HISTORIAL = ["numero_ficha", "fecha_entrada", "fecha_entrega", "estado",
                       "matricula", "marca_modelo", "kilometros", "combustible",
                       "recoger_piezas", "nombre", "cif", "telefono", "domicilio",
                       "numero", "cp", "poblacion", "reparaciones"]


# ===========================================================================
# EXPORTAR
# ===========================================================================

def _a_descarga(cabeceras, filas):
    """
    Construye el CSV en memoria y lo devuelve como BytesIO. 'filas' es una lista
    de diccionarios. Las claves que no estén en 'cabeceras' se ignoran
    (extrasaction="ignore"), así no se exporta el id interno de la tabla.
    """
    texto = io.StringIO()
    escritor = csv.DictWriter(texto, fieldnames=cabeceras, delimiter=_SEP,
                              extrasaction="ignore")
    escritor.writeheader()
    for fila in filas:
        escritor.writerow(fila)
    datos = texto.getvalue().encode(_CODIFICACION)   # a bytes, con BOM
    return io.BytesIO(datos)


def exportar_clientes(con):
    filas = [dict(f) for f in cliente.listar_todos(con)]
    return _a_descarga(CABECERAS_CLIENTES, filas)


def exportar_vehiculos(con):
    filas = [dict(f) for f in vehiculo.listar_todos_con_cliente(con)]
    return _a_descarga(CABECERAS_VEHICULOS, filas)


def exportar_historial(con):
    filas = [dict(f) for f in incidencia.listar_completo(con)]
    return _a_descarga(CABECERAS_HISTORIAL, filas)


# ===========================================================================
# IMPORTAR
# ===========================================================================

def _leer_filas(archivo):
    """
    Lee el fichero subido y devuelve (filas, error).
    'filas' es una lista de diccionarios (uno por línea, con la cabecera como
    claves); 'error' es un mensaje para el usuario, o None si todo va bien.
    """
    if archivo is None or archivo.filename == "":
        return [], "No se ha seleccionado ningún archivo."
    try:
        texto = archivo.read().decode(_CODIFICACION)
    except UnicodeDecodeError:
        return [], "El archivo no está en texto UTF-8."
    filas = list(csv.DictReader(io.StringIO(texto), delimiter=_SEP))
    if not filas:
        return [], "El archivo no tiene filas de datos."
    return filas, None


def _campo(fila, clave):
    """Devuelve fila[clave] sin espacios alrededor, o '' si no viene."""
    return (fila.get(clave) or "").strip()


def importar_clientes(con, archivo):
    """
    Importa clientes. Si el CIF ya existe, actualiza ese cliente; si no (o está
    vacío), lo da de alta. Las filas que no pasan las validaciones se descartan.
    Devuelve un resumen {anadidos, actualizados, descartados, errores}.
    """
    filas, error = _leer_filas(archivo)
    if error:
        return {"error": error}

    resumen = {"anadidos": 0, "actualizados": 0, "descartados": 0, "errores": []}
    for n, fila in enumerate(filas, start=2):   # la fila 1 es la cabecera
        datos = {c: _campo(fila, c) for c in CABECERAS_CLIENTES}
        datos["cif"] = datos["cif"].upper()
        problema = _validar_cliente(datos)
        if problema:
            _descartar(resumen, n, problema)
            continue

        existente = cliente.obtener_por_cif(con, datos["cif"]) if datos["cif"] else None
        if existente:
            cliente.actualizar(con, existente["id"], datos)
            resumen["actualizados"] += 1
        else:
            cliente.crear(con, datos)
            resumen["anadidos"] += 1
    return resumen


def importar_vehiculos(con, archivo):
    """
    Importa vehículos. Cada fila trae matrícula, marca/modelo y el CIF del dueño
    (cif_cliente), que tiene que existir ya. Si la matrícula existe, actualiza su
    marca/modelo; si no, da de alta el vehículo enlazándolo con su cliente.
    """
    filas, error = _leer_filas(archivo)
    if error:
        return {"error": error}

    resumen = {"anadidos": 0, "actualizados": 0, "descartados": 0, "errores": []}
    for n, fila in enumerate(filas, start=2):
        matricula   = validaciones.normalizar_matricula(_campo(fila, "matricula"))
        marca       = _campo(fila, "marca_modelo")
        cif_cliente = _campo(fila, "cif_cliente").upper()

        if not matricula or not validaciones.validar_matricula(matricula):
            _descartar(resumen, n, "la matrícula falta o no es válida.")
            continue
        if not marca:
            _descartar(resumen, n, "falta la marca y el modelo.")
            continue

        veh = vehiculo.obtener_por_matricula(con, matricula)
        if veh:
            vehiculo.actualizar_marca_modelo(con, veh["id"], marca)
            resumen["actualizados"] += 1
        else:
            dueno = cliente.obtener_por_cif(con, cif_cliente) if cif_cliente else None
            if dueno is None:
                _descartar(resumen, n,
                           f"no hay ningún cliente con CIF {cif_cliente or '(vacío)'}.")
                continue
            vehiculo.crear(con, matricula, marca, dueno["id"])
            resumen["anadidos"] += 1
    return resumen


def importar_historial(con, archivo):
    """
    Importa fichas (historial). Cada fila trae cliente, vehículo y ficha, igual
    que el formulario. Como al guardar a mano: si la matrícula existe, reaprovecha
    el coche y su cliente; si no, los crea. Cada fila añade una ficha nueva. Las
    reparaciones vienen en una celda separadas por '|'.
    """
    filas, error = _leer_filas(archivo)
    if error:
        return {"error": error}

    resumen = {"anadidos": 0, "descartados": 0, "errores": []}
    for n, fila in enumerate(filas, start=2):
        datos = {
            "fecha_entrada":  _campo(fila, "fecha_entrada"),
            "fecha_entrega":  _campo(fila, "fecha_entrega"),
            "nombre":         _campo(fila, "nombre"),
            "cif":            _campo(fila, "cif").upper(),
            "telefono":       _campo(fila, "telefono"),
            "domicilio":      _campo(fila, "domicilio"),
            "numero":         _campo(fila, "numero"),
            "cp":             _campo(fila, "cp"),
            "poblacion":      _campo(fila, "poblacion"),
            "marca_modelo":   _campo(fila, "marca_modelo"),
            "matricula":      validaciones.normalizar_matricula(_campo(fila, "matricula")),
            "kilometros":     _campo(fila, "kilometros"),
            "combustible":    _campo(fila, "combustible") or "1/2",
            "recoger_piezas": _campo(fila, "recoger_piezas") or "No",
        }
        problema = _validar_historial(datos)
        if problema:
            _descartar(resumen, n, problema)
            continue

        # Reparaciones: en el CSV van en una celda, separadas por '|'.
        reparaciones = [t.strip() for t in _campo(fila, "reparaciones").split("|")
                        if t.strip()]

        # Crear o reaprovechar cliente + vehículo por matrícula (misma lógica
        # que al guardar desde el formulario, en rutas/incidencias.py).
        veh = vehiculo.obtener_por_matricula(con, datos["matricula"])
        if veh:
            vehiculo_id = veh["id"]
            cliente.actualizar(con, veh["cliente_id"], datos)
            vehiculo.actualizar_marca_modelo(con, vehiculo_id, datos["marca_modelo"])
        else:
            cliente_id = cliente.crear(con, datos)
            vehiculo_id = vehiculo.crear(
                con, datos["matricula"], datos["marca_modelo"], cliente_id)

        # Estado: si en el CSV viene uno válido lo respetamos; si no, 'recepcionado'.
        estado = _campo(fila, "estado")
        if estado not in incidencia.ESTADOS:
            estado = "recepcionado"

        inc_id = incidencia.crear(con, {
            "vehiculo_id":    vehiculo_id,
            "fecha_entrada":  datos["fecha_entrada"],
            "fecha_entrega":  datos["fecha_entrega"] or None,
            "kilometros":     int(datos["kilometros"]) if datos["kilometros"] else None,
            "combustible":    datos["combustible"],
            "estado":         estado,
            "recoger_piezas": datos["recoger_piezas"],
        })
        reparacion.crear_varias(con, inc_id, reparaciones)
        resumen["anadidos"] += 1
    return resumen


# ---------------------------------------------------------------------------
# Ayudas internas de validación de filas.
# ---------------------------------------------------------------------------

def _descartar(resumen, fila, motivo):
    """Suma una fila descartada y guarda el motivo (solo los primeros, para no
    llenar la pantalla)."""
    resumen["descartados"] += 1
    if len(resumen["errores"]) < 5:
        resumen["errores"].append(f"Fila {fila}: {motivo}")


def _validar_cliente(datos):
    """Devuelve un mensaje si la fila de cliente no es válida, o '' si lo es."""
    if not datos["nombre"]:
        return "falta el nombre."
    if not validaciones.validar_documento(datos["cif"]):
        return "el DNI/CIF no es válido."
    if not validaciones.validar_telefono(datos["telefono"]):
        return "el teléfono no es válido."
    if not validaciones.validar_cp(datos["cp"]):
        return "el código postal no es válido."
    return ""


def _validar_historial(datos):
    """
    Comprueba una fila del historial; devuelve un mensaje de error o ''. Aquí la
    fecha de entrega es opcional (una ficha en reparación aún no la tiene).
    """
    if not datos["fecha_entrada"] or not validaciones.validar_fecha(datos["fecha_entrada"]):
        return "la fecha de entrada falta o no es válida."
    if datos["fecha_entrega"]:
        if not validaciones.validar_fecha(datos["fecha_entrega"]):
            return "la fecha de entrega no es válida."
        if not validaciones.fecha_entrega_coherente(datos["fecha_entrada"],
                                                    datos["fecha_entrega"]):
            return "la entrega es anterior a la entrada."
    if not datos["nombre"]:
        return "falta el nombre del cliente."
    if not datos["marca_modelo"]:
        return "falta la marca y el modelo."
    if not datos["matricula"] or not validaciones.validar_matricula(datos["matricula"]):
        return "la matrícula falta o no es válida."
    if not validaciones.validar_documento(datos["cif"]):
        return "el DNI/CIF no es válido."
    if not validaciones.validar_telefono(datos["telefono"]):
        return "el teléfono no es válido."
    if not validaciones.validar_cp(datos["cp"]):
        return "el código postal no es válido."
    if not validaciones.validar_kilometros(datos["kilometros"]):
        return "los kilómetros deben ser solo números."
    return ""
