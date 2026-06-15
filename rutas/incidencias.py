"""
Rutas de las incidencias (las órdenes de trabajo / resguardos de depósito).

Aquí está el formulario para dar de alta una incidencia y la generación del
resguardo en pantalla.

De momento NO guardamos nada en la base de datos: el formulario se valida y,
si todo es correcto, se muestra el resguardo ya relleno y listo para imprimir.
El guardado en la BD lo añadimos en el siguiente bloque del proyecto.
"""

from datetime import date, timedelta

from flask import Blueprint, render_template, request

from servicios.validaciones import validar_incidencia

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
        # 5 líneas de reparación vacías (como las 5 líneas del formulario en papel).
        "reparaciones":   ["", "", "", "", ""],
    }


@bp_incidencias.route("/nueva", methods=["GET", "POST"])
def nueva():
    # GET: mostramos el formulario con los valores por defecto.
    if request.method == "GET":
        return render_template(
            "incidencia_form.html",
            datos=_valores_por_defecto(),
            errores={},
        )

    # POST: el usuario ha pulsado "Generar resguardo".
    # 1) Recogemos lo que ha escrito y lo dejamos en un diccionario normal.
    datos = _leer_formulario(request.form)

    # 2) Lo validamos en el servidor (esta es la validación que de verdad
    #    cuenta; la del navegador solo avisa antes, pero no nos fiamos de ella).
    errores = validar_incidencia(datos)

    # 3) Si hay errores, volvemos a mostrar el formulario con lo que ya había
    #    escrito y los mensajes de error junto a cada campo.
    if errores:
        return render_template(
            "incidencia_form.html",
            datos=datos,
            errores=errores,
        )

    # 4) Si todo está bien: nos quedamos solo con las líneas de reparación
    #    que llevan texto y mostramos el resguardo relleno.
    datos["reparaciones"] = [linea for linea in datos["reparaciones"] if linea]
    return render_template("resguardo.html", datos=datos)


def _leer_formulario(form):
    """
    Pasa los datos del formulario (un objeto de Flask) a un diccionario
    normal, que es más cómodo de manejar y de enviar a la plantilla.
    De paso, limpia los espacios y pone en mayúsculas el DNI y la matrícula.
    """
    matricula = form.get("matricula", "").upper().replace("-", "").replace(" ", "")
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
        "matricula":      matricula.strip(),
        "kilometros":     form.get("kilometros", "").strip(),
        "combustible":    form.get("combustible", "1/2"),
        "recoger_piezas": form.get("recoger_piezas", "No"),
        # getlist recoge TODAS las casillas que se llaman "reparacion".
        "reparaciones":   [r.strip() for r in form.getlist("reparacion")],
    }
