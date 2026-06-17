"""
Gestión de vehículos (CRUD: listar, crear, editar y borrar).

Cada vehículo pertenece a un cliente, que se elige de un desplegable. La
matrícula identifica al coche: al crear se comprueba que no esté repetida y al
editar no se puede cambiar. No se deja borrar un vehículo con fichas.
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)

from modelos.conexion import obtener_conexion
from modelos import cliente, vehiculo, incidencia
from servicios.validaciones import validar_vehiculo, normalizar_matricula

bp_vehiculos = Blueprint("vehiculos", __name__, url_prefix="/vehiculos")


@bp_vehiculos.route("/")
def lista():
    """Listado de vehículos con su dueño y cuántas fichas tienen."""
    con = obtener_conexion()
    try:
        vehiculos = vehiculo.listar_con_resumen(con)
    finally:
        con.close()
    return render_template("vehiculos_lista.html", vehiculos=vehiculos)


@bp_vehiculos.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    con = obtener_conexion()

    if request.method == "POST":
        datos = _leer_formulario(request.form)
        errores = validar_vehiculo(datos)
        # Comprobaciones que dependen de la base de datos (no del formato):
        if "matricula" not in errores and vehiculo.obtener_por_matricula(con, datos["matricula"]):
            errores["matricula"] = "Ya existe un vehículo con esa matrícula."
        if not datos["cliente_id"]:
            errores["cliente_id"] = "Elige el cliente dueño del vehículo."

        if not errores:
            vehiculo.crear(con, datos["matricula"], datos["marca_modelo"],
                           int(datos["cliente_id"]))
            con.commit()
            con.close()
            flash("Vehículo creado correctamente.", "exito")
            return redirect(url_for("vehiculos.lista"))

        clientes = cliente.listar_todos(con)
        con.close()
        return render_template("vehiculo_form.html", datos=datos, errores=errores,
                               clientes=clientes, modo="nuevo")

    clientes = cliente.listar_todos(con)
    con.close()
    return render_template("vehiculo_form.html", datos={}, errores={},
                           clientes=clientes, modo="nuevo")


@bp_vehiculos.route("/<int:vehiculo_id>/editar", methods=["GET", "POST"])
def editar(vehiculo_id):
    con = obtener_conexion()
    fila = vehiculo.obtener_por_id(con, vehiculo_id)
    if fila is None:
        con.close()
        abort(404)

    if request.method == "POST":
        datos = _leer_formulario(request.form)
        # La matrícula no se edita: uso siempre la que ya tiene el coche.
        datos["matricula"] = fila["matricula"]
        errores = validar_vehiculo(datos)
        if not datos["cliente_id"]:
            errores["cliente_id"] = "Elige el cliente dueño del vehículo."

        if not errores:
            vehiculo.actualizar(con, vehiculo_id, datos["marca_modelo"],
                                int(datos["cliente_id"]))
            con.commit()
            con.close()
            flash("Vehículo actualizado.", "exito")
            return redirect(url_for("vehiculos.lista"))

        clientes = cliente.listar_todos(con)
        con.close()
        datos["id"] = vehiculo_id
        return render_template("vehiculo_form.html", datos=datos, errores=errores,
                               clientes=clientes, modo="editar")

    clientes = cliente.listar_todos(con)
    datos = dict(fila)
    con.close()
    return render_template("vehiculo_form.html", datos=datos, errores={},
                           clientes=clientes, modo="editar")


@bp_vehiculos.route("/<int:vehiculo_id>/borrar", methods=["POST"])
def borrar(vehiculo_id):
    """Borra un vehículo, solo si no tiene fichas en el historial."""
    con = obtener_conexion()
    try:
        fila = vehiculo.obtener_por_id(con, vehiculo_id)
        if fila is None:
            abort(404)
        n = incidencia.contar_por_vehiculo(con, vehiculo_id)
        if n > 0:
            flash(f"No se puede borrar el vehículo {fila['matricula']}: "
                  f"tiene {n} ficha(s) en el historial.", "error")
        else:
            vehiculo.borrar(con, vehiculo_id)
            con.commit()
            flash("Vehículo borrado.", "exito")
    finally:
        con.close()
    return redirect(url_for("vehiculos.lista"))


def _leer_formulario(form):
    """Pasa el formulario a un diccionario, normalizando la matrícula."""
    return {
        "matricula":    normalizar_matricula(form.get("matricula", "")),
        "marca_modelo": form.get("marca_modelo", "").strip(),
        "cliente_id":   form.get("cliente_id", "").strip(),
    }
