"""
Gestión de clientes (CRUD: listar, crear, editar y borrar).

Mismo patrón que las incidencias: GET muestra el formulario, POST valida y
guarda, y luego redirige. No se deja borrar un cliente con vehículos, para no
perder por error el historial de un coche.
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)

from modelos.conexion import obtener_conexion
from modelos import cliente, vehiculo
from servicios.validaciones import validar_cliente

bp_clientes = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp_clientes.route("/")
def lista():
    """Listado de clientes con cuántos coches tiene cada uno."""
    con = obtener_conexion()
    try:
        clientes = cliente.listar_con_resumen(con)
    finally:
        con.close()
    return render_template("clientes_lista.html", clientes=clientes)


@bp_clientes.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "GET":
        return render_template("cliente_form.html",
                               datos={}, errores={}, modo="nuevo")

    datos = _leer_formulario(request.form)
    errores = validar_cliente(datos)
    if errores:
        return render_template("cliente_form.html",
                               datos=datos, errores=errores, modo="nuevo")

    con = obtener_conexion()
    try:
        cliente.crear(con, datos)
        con.commit()
    finally:
        con.close()
    flash("Cliente creado correctamente.", "exito")
    return redirect(url_for("clientes.lista"))


@bp_clientes.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
def editar(cliente_id):
    con = obtener_conexion()
    fila = cliente.obtener_por_id(con, cliente_id)
    if fila is None:
        con.close()
        abort(404)

    if request.method == "POST":
        datos = _leer_formulario(request.form)
        errores = validar_cliente(datos)
        if not errores:
            cliente.actualizar(con, cliente_id, datos)
            con.commit()
            con.close()
            flash("Cliente actualizado.", "exito")
            return redirect(url_for("clientes.lista"))
        con.close()
        datos["id"] = cliente_id   # el formulario lo necesita para el action
        return render_template("cliente_form.html",
                               datos=datos, errores=errores, modo="editar")

    con.close()
    return render_template("cliente_form.html",
                           datos=dict(fila), errores={}, modo="editar")


@bp_clientes.route("/<int:cliente_id>/borrar", methods=["POST"])
def borrar(cliente_id):
    """
    Borra un cliente, solo si no tiene vehículos. Si los tiene, no borra y avisa.
    """
    con = obtener_conexion()
    try:
        fila = cliente.obtener_por_id(con, cliente_id)
        if fila is None:
            abort(404)
        n = vehiculo.contar_por_cliente(con, cliente_id)
        if n > 0:
            flash(f"No se puede borrar «{fila['nombre']}»: tiene {n} vehículo(s). "
                  "Borra o reasigna antes sus coches.", "error")
        else:
            cliente.borrar(con, cliente_id)
            con.commit()
            flash("Cliente borrado.", "exito")
    finally:
        con.close()
    return redirect(url_for("clientes.lista"))


def _leer_formulario(form):
    """Pasa el formulario a un diccionario, limpiando espacios y subiendo el CIF a mayúsculas."""
    return {
        "nombre":    form.get("nombre", "").strip(),
        "cif":       form.get("cif", "").strip().upper(),
        "telefono":  form.get("telefono", "").strip(),
        "domicilio": form.get("domicilio", "").strip(),
        "numero":    form.get("numero", "").strip(),
        "cp":        form.get("cp", "").strip(),
        "poblacion": form.get("poblacion", "").strip(),
    }
