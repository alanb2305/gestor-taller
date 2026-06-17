"""
Rutas de las incidencias (las órdenes de trabajo / resguardos de depósito):
el alta de una ficha, el guardado, la vista del resguardo, sus fotos, el
historial y el endpoint que usa el autorrelleno.

Al guardar valido primero en el servidor y solo escribo si todo está bien. El
guardado va en una única transacción: o se graba todo (cliente, vehículo,
incidencia y reparaciones) o no se graba nada.
"""

from datetime import date, timedelta

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort, jsonify, send_file,
                   send_from_directory)

from config import DIR_FOTOS
from modelos.conexion import obtener_conexion
from modelos import cliente, vehiculo, incidencia, reparacion, foto
from servicios.validaciones import validar_incidencia, normalizar_matricula
from servicios.pdf import generar_resguardo_pdf
from servicios import fotos

# url_prefix: todas las rutas de este blueprint empiezan por /incidencias.
bp_incidencias = Blueprint("incidencias", __name__, url_prefix="/incidencias")


def _valores_por_defecto():
    """
    Valores con los que se abre el formulario: hoy como fecha de entrada y tres
    días después como entrega prevista (igual que el programa de escritorio).
    """
    hoy = date.today()
    return {
        # isoformat() da AAAA-MM-DD, que es lo que entiende el <input type="date">.
        "fecha_entrada":  hoy.isoformat(),
        "fecha_entrega":  (hoy + timedelta(days=3)).isoformat(),
        "nombre":         "",
        "cif":            "",
        "telefono":       "",
        "domicilio":      "",
        "numero":         "",
        "cp":             "",
        "poblacion":      "",
        "marca_modelo":   "",
        "matricula":      "",
        "kilometros":     "",
        "combustible":    "1/2",
        "recoger_piezas": "No",
        # Una línea al empezar; el usuario añade más con el botón "+" (trabajos.js).
        "reparaciones":   [""],
    }


@bp_incidencias.route("/nueva", methods=["GET", "POST"])
def nueva():
    # GET: formulario con los valores por defecto.
    if request.method == "GET":
        return render_template("incidencia_form.html",
                               datos=_valores_por_defecto(), errores={})

    # POST: recogemos lo escrito y lo validamos en el servidor.
    datos = _leer_formulario(request.form)
    errores = validar_incidencia(datos)
    if errores:
        # Volvemos al formulario conservando lo escrito y los errores.
        return render_template("incidencia_form.html",
                               datos=datos, errores=errores)

    # Nos quedamos solo con las líneas de reparación que tienen texto.
    datos["reparaciones"] = [linea for linea in datos["reparaciones"] if linea]

    con = obtener_conexion()
    try:
        incidencia_id = _guardar_incidencia(con, datos)
        # Las fotos de los daños se adjuntan en el mismo formulario (multipart).
        # Las guardo dentro de la misma transacción que la ficha: si algo falla,
        # no se queda nada a medias.
        subidas, descartadas = _guardar_fotos(
            con, incidencia_id, request.files.getlist("fotos"))
        con.commit()
    except Exception:
        # Si algo falla a mitad, deshacemos para no dejar datos a medias.
        con.rollback()
        flash("No se ha podido guardar la ficha. Inténtalo de nuevo.", "error")
        return render_template("incidencia_form.html",
                               datos=datos, errores={})
    finally:
        con.close()

    # Después de guardar redirijo al resguardo (en vez de devolver el HTML), así
    # si el usuario recarga la página no se guarda otra ficha repetida.
    mensaje = "Ficha guardada correctamente."
    if subidas:
        mensaje += f" {subidas} foto(s) de los daños añadida(s)."
    if descartadas:
        mensaje += f" {descartadas} descartada(s) por tipo o tamaño."
    flash(mensaje, "exito")
    return redirect(url_for("incidencias.resguardo", incidencia_id=incidencia_id))


@bp_incidencias.route("/matricula/<matricula>")
def buscar_matricula(matricula):
    """
    Endpoint del autorrelleno (lo llama static/js/autorrelleno.js): devuelve en
    JSON los datos del cliente y del vehículo de una matrícula ya registrada. Si
    la matrícula es nueva responde {"encontrado": false}. No devuelvo los ids
    internos: al navegador solo le hacen falta los campos a rellenar.
    """
    # Normalizo igual que al guardar para que "1234-bcd" y "1234 BCD" encuentren
    # la misma matrícula.
    matricula = normalizar_matricula(matricula)

    con = obtener_conexion()
    try:
        fila = vehiculo.datos_para_autorrelleno(con, matricula)
    finally:
        con.close()

    if fila is None:
        return jsonify({"encontrado": False})

    return jsonify({
        "encontrado":   True,
        "nombre":       fila["nombre"],
        "cif":          fila["cif"],
        "telefono":     fila["telefono"],
        "domicilio":    fila["domicilio"],
        "numero":       fila["numero"],
        "cp":           fila["cp"],
        "poblacion":    fila["poblacion"],
        "marca_modelo": fila["marca_modelo"],
    })


@bp_incidencias.route("/<int:incidencia_id>")
def resguardo(incidencia_id):
    """Muestra el resguardo de una ficha ya guardada, listo para imprimir."""
    con = obtener_conexion()
    try:
        datos = _datos_resguardo(con, incidencia_id)
        # Las fotos se gestionan desde el resguardo (aquí la ficha ya tiene id).
        # El PDF no las usa, por eso las cargo aparte y solo si la ficha existe.
        fotos_ficha = (foto.listar_por_incidencia(con, incidencia_id)
                       if datos is not None else [])
    finally:
        con.close()

    if datos is None:
        abort(404)   # la ficha no existe (id inventado en la URL)
    return render_template("resguardo.html", datos=datos, fotos=fotos_ficha)


@bp_incidencias.route("/<int:incidencia_id>/pdf")
def descargar_pdf(incidencia_id):
    """
    Genera el resguardo en PDF y lo descarga. Usa los mismos datos que la vista
    en pantalla. El PDF se crea en memoria con reportlab (no se guarda ningún
    fichero en el servidor). Es la alternativa al botón "Imprimir" del navegador.
    """
    con = obtener_conexion()
    try:
        datos = _datos_resguardo(con, incidencia_id)
    finally:
        con.close()

    if datos is None:
        abort(404)

    pdf = generar_resguardo_pdf(datos)
    nombre = f"resguardo_{datos['matricula']}_{datos['id']:05d}.pdf"
    return send_file(pdf, mimetype="application/pdf",
                     as_attachment=True, download_name=nombre)


# ---------------------------------------------------------------------------
# Fotos de los daños de una ficha (subir, borrar y servir cada imagen). La
# validación de tipo y tamaño la hace servicios/fotos.py, y la imagen se sirve
# con send_from_directory para no construir rutas a mano (evita path traversal).
# ---------------------------------------------------------------------------

@bp_incidencias.route("/<int:incidencia_id>/fotos", methods=["POST"])
def subir_fotos(incidencia_id):
    """
    Añade más fotos de los daños a una ficha ya guardada (desde el resguardo).
    Las fotos del estado del coche se suben al crear la ficha; esto es para
    agregar alguna más después. Dejo un flash con el resumen y vuelvo al resguardo.
    """
    con = obtener_conexion()
    try:
        # La ficha tiene que existir para colgarle fotos.
        if incidencia.obtener_estado(con, incidencia_id) is None:
            abort(404)
        subidas, descartadas = _guardar_fotos(
            con, incidencia_id, request.files.getlist("fotos"))
        con.commit()
    finally:
        con.close()

    if subidas:
        mensaje = f"{subidas} foto(s) subida(s)."
        if descartadas:
            mensaje += f" {descartadas} descartada(s) por tipo o tamaño."
        flash(mensaje, "exito")
    elif descartadas:
        flash(f"No se ha subido ninguna foto: {descartadas} descartada(s) por "
              "tipo o tamaño (se admiten JPG, PNG o WEBP de hasta 5 MB).",
              "error")
    else:
        flash("No has seleccionado ninguna foto.", "error")

    return redirect(url_for("incidencias.resguardo", incidencia_id=incidencia_id))


@bp_incidencias.route("/<int:incidencia_id>/fotos/<int:foto_id>/borrar",
                      methods=["POST"])
def borrar_foto(incidencia_id, foto_id):
    """
    Borra una foto: primero la fila de la base de datos y luego su archivo.
    Es POST porque cambia datos. Después vuelve al resguardo.
    """
    con = obtener_conexion()
    try:
        fila = foto.obtener_por_id(con, foto_id)
        # Compruebo que la foto existe y que es de ESTA ficha (para que el id de
        # la URL no apunte a la foto de otra incidencia).
        if fila is None or fila["incidencia_id"] != incidencia_id:
            abort(404)
        foto.borrar(con, foto_id)
        con.commit()
        # Borro el fichero después de confirmar el borrado en la base de datos.
        fotos.borrar_archivo(fila["nombre_archivo"])
        flash("Foto borrada.", "exito")
    finally:
        con.close()

    return redirect(url_for("incidencias.resguardo", incidencia_id=incidencia_id))


@bp_incidencias.route("/<int:incidencia_id>/foto/<int:foto_id>")
def ver_foto(incidencia_id, foto_id):
    """
    Sirve el archivo de una foto con send_from_directory, que garantiza que el
    nombre no se salga de DIR_FOTOS (evita path traversal).
    """
    con = obtener_conexion()
    try:
        fila = foto.obtener_por_id(con, foto_id)
    finally:
        con.close()

    if fila is None or fila["incidencia_id"] != incidencia_id:
        abort(404)
    return send_from_directory(DIR_FOTOS, fila["nombre_archivo"])


@bp_incidencias.route("/historial")
def historial():
    """
    Lista de fichas guardadas. Si llega el parámetro de búsqueda 'q', filtra
    por matrícula, nombre o fecha; si no, muestra las últimas.
    """
    busqueda = request.args.get("q", "").strip()
    con = obtener_conexion()
    try:
        fichas = incidencia.buscar(con, busqueda) if busqueda else incidencia.listar(con)
    finally:
        con.close()

    # Para cada estado, cuál es el siguiente. Lo calculamos una vez aquí y la
    # plantilla lo usa para poner en cada fila el botón "pasar a <siguiente>".
    siguiente_estado = {e: incidencia.siguiente_estado(e)
                        for e in incidencia.ESTADOS}

    return render_template("historial.html", fichas=fichas,
                           busqueda=busqueda, siguiente_estado=siguiente_estado)


@bp_incidencias.route("/<int:incidencia_id>/estado", methods=["POST"])
def avanzar_estado(incidencia_id):
    """
    Pasa una ficha al siguiente estado (recepcionado -> en reparación ->
    terminado -> entregado). Es POST porque cambia datos. El estado destino lo
    decide el servidor a partir del actual: el navegador solo pide "avanzar".
    """
    con = obtener_conexion()
    try:
        estado = incidencia.obtener_estado(con, incidencia_id)
        if estado is None:
            abort(404)   # la ficha no existe (id inventado en la URL)

        siguiente = incidencia.siguiente_estado(estado)
        if siguiente is not None:
            incidencia.cambiar_estado(con, incidencia_id, siguiente)
            con.commit()
            flash(f"Ficha n.º {incidencia_id:05d} marcada como «{siguiente}».",
                  "exito")
        # Si ya estaba en el último estado no hacemos nada (el botón ni se muestra).
    finally:
        con.close()

    return redirect(url_for("incidencias.historial"))


def _guardar_incidencia(con, datos):
    """
    Graba una ficha completa y devuelve el id de la incidencia. La matrícula
    identifica al coche (es UNIQUE): si ya existe, reutilizo ese vehículo y su
    cliente y pongo al día sus datos; si no, creo cliente y vehículo nuevos.
    Al final van la incidencia y sus reparaciones.
    """
    veh = vehiculo.obtener_por_matricula(con, datos["matricula"])
    if veh:
        vehiculo_id = veh["id"]
        # La matrícula ya estaba: actualizo los datos del cliente y la marca/modelo
        # por si se han corregido al rellenar la ficha.
        cliente.actualizar(con, veh["cliente_id"], datos)
        vehiculo.actualizar_marca_modelo(con, vehiculo_id, datos["marca_modelo"])
    else:
        cliente_id = cliente.crear(con, datos)
        vehiculo_id = vehiculo.crear(
            con, datos["matricula"], datos["marca_modelo"], cliente_id)

    incidencia_id = incidencia.crear(con, {
        "vehiculo_id":    vehiculo_id,
        "fecha_entrada":  datos["fecha_entrada"],
        "fecha_entrega":  datos["fecha_entrega"] or None,
        # Los kilómetros son enteros en la BD: convierto el texto (ya validado)
        # o dejo None si viene vacío.
        "kilometros":     int(datos["kilometros"]) if datos["kilometros"] else None,
        "combustible":    datos["combustible"],
        "estado":         "recepcionado",
        "recoger_piezas": datos["recoger_piezas"],
    })
    reparacion.crear_varias(con, incidencia_id, datos["reparaciones"])
    return incidencia_id


def _guardar_fotos(con, incidencia_id, archivos):
    """
    Guarda las fotos válidas de una ficha (las que pasan el control de tipo y
    tamaño de servicios/fotos.py) y devuelve (subidas, descartadas) para el
    aviso. No hace commit ni cierra la conexión: de eso se encarga quien llama.
    La usan el alta de la ficha y el formulario de fotos del resguardo.
    """
    # getlist trae todos los ficheros del input (lleva 'multiple'); me quedo con
    # los que traen nombre (al enviar sin elegir nada, llega un hueco vacío).
    archivos = [a for a in archivos if a and a.filename]
    subidas = 0
    for archivo in archivos:
        nombre = fotos.guardar(archivo)
        if nombre:
            foto.crear(con, incidencia_id, nombre)
            subidas += 1
    return subidas, len(archivos) - subidas


def _datos_resguardo(con, incidencia_id):
    """
    Carga una incidencia completa (cliente, vehículo y reparaciones) en un
    diccionario listo para la plantilla y el PDF, o None si no existe. Lo usan
    la vista del resguardo y la descarga en PDF, para no repetir el trabajo.
    """
    fila = incidencia.obtener_completa(con, incidencia_id)
    if fila is None:
        return None
    lineas = reparacion.listar_por_incidencia(con, incidencia_id)
    datos = dict(fila)
    datos["reparaciones"] = [linea["descripcion"] for linea in lineas]
    return datos


def _leer_formulario(form):
    """
    Pasa los datos del formulario a un diccionario normal, más cómodo de manejar.
    De paso limpia los espacios y pone en mayúsculas el DNI y la matrícula.
    """
    return {
        "fecha_entrada":  form.get("fecha_entrada", "").strip(),
        "fecha_entrega":  form.get("fecha_entrega", "").strip(),
        "nombre":         form.get("nombre", "").strip(),
        "cif":            form.get("cif", "").strip().upper(),
        "telefono":       form.get("telefono", "").strip(),
        "domicilio":      form.get("domicilio", "").strip(),
        "numero":         form.get("numero", "").strip(),
        "cp":             form.get("cp", "").strip(),
        "poblacion":      form.get("poblacion", "").strip(),
        "marca_modelo":   form.get("marca_modelo", "").strip(),
        # normalizar_matricula la deja en mayúsculas y sin guiones ni espacios.
        "matricula":      normalizar_matricula(form.get("matricula", "")),
        "kilometros":     form.get("kilometros", "").strip(),
        "combustible":    form.get("combustible", "1/2"),
        "recoger_piezas": form.get("recoger_piezas", "No"),
        # getlist recoge todas las casillas que se llaman "reparacion".
        "reparaciones":   [r.strip() for r in form.getlist("reparacion")],
    }
