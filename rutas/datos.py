"""
Rutas de importar / exportar datos en CSV (clientes, vehículos e historial),
para llevar los datos a Excel y volver a traerlos. La lógica de leer y escribir
el CSV está en servicios/csv_datos.py; aquí abro la conexión, llamo al servicio
y, al importar, confirmo o deshago la transacción y dejo un mensaje.
"""

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, send_file)

from modelos.conexion import obtener_conexion
from servicios import csv_datos

bp_datos = Blueprint("datos", __name__, url_prefix="/datos")


@bp_datos.route("/")
def panel():
    """Pantalla con los botones de exportar y los formularios de importar."""
    return render_template("datos.html")


# ---------------------------------------------------------------------------
# Exportar (descargas). Son GET: no cambian nada, solo leen y devuelven el CSV.
# ---------------------------------------------------------------------------

@bp_datos.route("/exportar/clientes.csv")
def exportar_clientes():
    con = obtener_conexion()
    csv_bytes = csv_datos.exportar_clientes(con)
    con.close()
    return send_file(csv_bytes, mimetype="text/csv",
                     as_attachment=True, download_name="clientes.csv")


@bp_datos.route("/exportar/vehiculos.csv")
def exportar_vehiculos():
    con = obtener_conexion()
    csv_bytes = csv_datos.exportar_vehiculos(con)
    con.close()
    return send_file(csv_bytes, mimetype="text/csv",
                     as_attachment=True, download_name="vehiculos.csv")


@bp_datos.route("/exportar/historial.csv")
def exportar_historial():
    con = obtener_conexion()
    csv_bytes = csv_datos.exportar_historial(con)
    con.close()
    return send_file(csv_bytes, mimetype="text/csv",
                     as_attachment=True, download_name="historial.csv")


# ---------------------------------------------------------------------------
# Importar (subidas). Son POST: cambian la base de datos.
# ---------------------------------------------------------------------------

def _procesar_importacion(funcion, archivo, nombre):
    """
    Parte común de las tres importaciones: abre la conexión, llama a la función
    de importación, confirma (o deshace si hay error) y deja un mensaje con el
    resumen. Después vuelve al panel.
    """
    con = obtener_conexion()
    try:
        resumen = funcion(con, archivo)
        if "error" in resumen:
            con.rollback()
            flash(f"No se pudo importar {nombre}: {resumen['error']}", "error")
            return redirect(url_for("datos.panel"))
        con.commit()
    except Exception:
        # Cualquier fallo inesperado: deshacemos para no dejar datos a medias.
        con.rollback()
        flash(f"Error inesperado al importar {nombre}. No se ha guardado nada.",
              "error")
        return redirect(url_for("datos.panel"))
    finally:
        con.close()

    # Montamos el mensaje de resumen (añadidos / actualizados / descartados).
    partes = []
    if "anadidos" in resumen:
        partes.append(f"{resumen['anadidos']} añadidos")
    if "actualizados" in resumen:
        partes.append(f"{resumen['actualizados']} actualizados")
    if "descartados" in resumen:
        partes.append(f"{resumen['descartados']} descartados")
    mensaje = f"Importación de {nombre}: " + ", ".join(partes) + "."
    if resumen.get("errores"):
        mensaje += "  Descartados (ejemplos): " + "  /  ".join(resumen["errores"])

    # Verde si entró algo; rojo si no se pudo añadir ni actualizar nada.
    hubo_cambios = resumen.get("anadidos", 0) + resumen.get("actualizados", 0) > 0
    flash(mensaje, "exito" if hubo_cambios else "error")
    return redirect(url_for("datos.panel"))


@bp_datos.route("/importar/clientes", methods=["POST"])
def importar_clientes():
    return _procesar_importacion(csv_datos.importar_clientes,
                                 request.files.get("archivo"), "clientes")


@bp_datos.route("/importar/vehiculos", methods=["POST"])
def importar_vehiculos():
    return _procesar_importacion(csv_datos.importar_vehiculos,
                                 request.files.get("archivo"), "vehículos")


@bp_datos.route("/importar/historial", methods=["POST"])
def importar_historial():
    return _procesar_importacion(csv_datos.importar_historial,
                                 request.files.get("archivo"), "historial")
