"""
Rutas de las incidencias (las órdenes de trabajo / resguardos de depósito).

Aquí está el alta de una ficha (el formulario), el guardado en la base de
datos, la vista del resguardo ya relleno, el historial de fichas y el
pequeño endpoint que usa el autorrelleno para traer los datos de una
matrícula ya conocida.

Al guardar seguimos el orden "comprobar primero, escribir después": primero
validamos en el servidor y, solo si todo está bien, abrimos la conexión y
escribimos. Todo el guardado va dentro de una única transacción: o se graba
el cliente, el vehículo, la incidencia y sus reparaciones, o no se graba nada.
"""

from datetime import date, timedelta

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort, jsonify, send_file)

from modelos.conexion import obtener_conexion
from modelos import cliente, vehiculo, incidencia, reparacion
from servicios.validaciones import validar_incidencia, normalizar_matricula
from servicios.pdf import generar_resguardo_pdf

# url_prefix: todas las rutas de este blueprint empiezan por /incidencias.
bp_incidencias = Blueprint("incidencias", __name__, url_prefix="/incidencias")


def _valores_por_defecto():
    """
    Valores con los que aparece el formulario al abrirlo: la fecha de hoy
    como entrada y tres días después como entrega prevista, igual que hacía
    el programa de escritorio original.
    """
    hoy = date.today()
    return {
        # isoformat() devuelve AAAA-MM-DD, que es justo lo que entiende
        # el <input type="date"> del navegador.
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
        # Una sola línea al empezar; el usuario añade más con el botón "+"
        # (lo gestiona static/js/trabajos.js).
        "reparaciones":   [""],
    }


@bp_incidencias.route("/nueva", methods=["GET", "POST"])
def nueva():
    # GET: formulario con los valores por defecto.
    if request.method == "GET":
        return render_template("incidencia_form.html",
                               datos=_valores_por_defecto(), errores={})

    # POST: recogemos lo escrito y lo validamos en el servidor (esta es la
    # validación que cuenta; la del navegador solo avisa antes de enviar).
    datos = _leer_formulario(request.form)
    errores = validar_incidencia(datos)
    if errores:
        # Volvemos al formulario conservando lo escrito y los mensajes de error.
        return render_template("incidencia_form.html",
                               datos=datos, errores=errores)

    # Nos quedamos solo con las líneas de reparación que llevan texto.
    datos["reparaciones"] = [linea for linea in datos["reparaciones"] if linea]

    # Guardado dentro de una transacción.
    con = obtener_conexion()
    try:
        incidencia_id = _guardar_incidencia(con, datos)
        con.commit()
    except Exception:
        # Si algo falla a mitad, deshacemos para no dejar datos a medias.
        con.rollback()
        flash("No se ha podido guardar la ficha. Inténtalo de nuevo.", "error")
        return render_template("incidencia_form.html",
                               datos=datos, errores={})
    finally:
        con.close()

    # Patrón Post/Redirect/Get: después de guardar redirigimos a la vista del
    # resguardo en vez de devolver el HTML directamente. Así, si el usuario
    # recarga la página, NO se vuelve a guardar otra ficha repetida.
    flash("Ficha guardada correctamente.", "exito")
    return redirect(url_for("incidencias.resguardo", incidencia_id=incidencia_id))


@bp_incidencias.route("/matricula/<matricula>")
def buscar_matricula(matricula):
    """
    Endpoint del autorrelleno (lo llama static/js/autorrelleno.js).

    Devuelve en JSON los datos del cliente y del vehículo de una matrícula
    que ya está registrada, para que el formulario los rellene solo. Si la
    matrícula es nueva, responde {"encontrado": false} y el formulario se
    deja como está.

    No devolvemos los ids internos de la base de datos: al navegador solo le
    hacen falta los campos que tiene que rellenar.
    """
    # Normalizamos igual que al guardar (mayúsculas, sin guiones ni espacios)
    # para que "1234-bcd" y "1234 BCD" encuentren la misma matrícula.
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
    finally:
        con.close()

    if datos is None:
        abort(404)   # la ficha no existe (id inventado en la URL)
    return render_template("resguardo.html", datos=datos)


@bp_incidencias.route("/<int:incidencia_id>/pdf")
def descargar_pdf(incidencia_id):
    """
    Genera el resguardo en PDF y lo descarga como archivo.

    Usa exactamente los mismos datos que la vista en pantalla (misma
    incidencia, mismo cliente y vehículo). El PDF se crea en memoria con
    reportlab y se envía como descarga; no se guarda ningún fichero en el
    servidor. El botón "Imprimir" de la pantalla sigue valiendo para imprimir
    o "guardar como PDF" desde el propio navegador; esto es la otra opción:
    bajarse el archivo directamente.
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
    Pasa una ficha al siguiente estado de su ciclo de trabajo
    (recibido -> en reparación -> terminado -> entregado).

    Es un POST porque cambia datos de la base de datos (con GET no se debe
    modificar nada). El estado destino lo decide el SERVIDOR a partir del
    estado actual: el navegador solo puede pedir "avanzar", no elegir a qué
    estado salta. Después volvemos al historial (patrón Post/Redirect/Get).
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
        # Si ya estaba en el último estado, no hacemos nada: el botón no se
        # muestra en ese caso y aquí solo se llegaría manipulando la URL.
    finally:
        con.close()

    return redirect(url_for("incidencias.historial"))


def _guardar_incidencia(con, datos):
    """
    Graba una ficha completa y devuelve el id de la incidencia creada.

    La matrícula identifica al coche (es UNIQUE en la tabla):
      - Si ya existe, reutilizamos ese vehículo y su cliente, y de paso
        ponemos al día sus datos con lo que se haya escrito en el formulario.
        Así, con el autorrelleno, se puede corregir un teléfono o un
        domicilio antiguo y queda guardado lo último.
      - Si no existe, creamos cliente nuevo y vehículo nuevo.
    Después va la incidencia y sus reparaciones.
    """
    veh = vehiculo.obtener_por_matricula(con, datos["matricula"])
    if veh:
        vehiculo_id = veh["id"]
        # La matrícula ya estaba: actualizamos los datos del cliente y la
        # marca/modelo por si se han corregido al rellenar la ficha.
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
        # En la BD los kilómetros son un número entero; convertimos el texto
        # (ya validado como dígitos) o dejamos None si viene vacío.
        "kilometros":     int(datos["kilometros"]) if datos["kilometros"] else None,
        "combustible":    datos["combustible"],
        "estado":         "recibido",
        "recoger_piezas": datos["recoger_piezas"],
    })
    reparacion.crear_varias(con, incidencia_id, datos["reparaciones"])
    return incidencia_id


def _datos_resguardo(con, incidencia_id):
    """
    Carga una incidencia completa (con su cliente y su vehículo) más sus
    líneas de reparación, y lo devuelve como un diccionario listo para la
    plantilla y para el PDF. Devuelve None si la ficha no existe.

    Lo usan la vista del resguardo y la descarga en PDF, así no repetimos en
    los dos sitios el mismo trabajo de juntar la incidencia con sus líneas.
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
    Pasa los datos del formulario (un objeto de Flask) a un diccionario
    normal, más cómodo de manejar y de enviar a la plantilla.
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
        # normalizar_matricula deja la matrícula en mayúsculas y sin guiones
        # ni espacios (la misma función que usan el autorrelleno y el CSV).
        "matricula":      normalizar_matricula(form.get("matricula", "")),
        "kilometros":     form.get("kilometros", "").strip(),
        "combustible":    form.get("combustible", "1/2"),
        "recoger_piezas": form.get("recoger_piezas", "No"),
        # getlist recoge TODAS las casillas que se llaman "reparacion".
        "reparaciones":   [r.strip() for r in form.getlist("reparacion")],
    }
