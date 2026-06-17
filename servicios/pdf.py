"""
Generación del resguardo en PDF con reportlab, a partir de los mismos datos de
la incidencia que se ven en pantalla. Trabajo con bloques (párrafos y tablas) y
dejo que reportlab los vaya colocando, en lugar de dibujar en coordenadas
exactas (más fácil de leer). El PDF se genera en memoria y se manda como
descarga; no se guarda ningún fichero en el servidor.
"""

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle, HRFlowable)

from config import TALLER
from servicios.formato import fecha_es

# Colores (los mismos tonos que la web, para que el PDF case con la pantalla).
_NARANJA    = colors.HexColor("#e07b00")
_GRIS       = colors.HexColor("#555555")
_GRIS_BORDE = colors.HexColor("#bbbbbb")
_GRIS_FONDO = colors.HexColor("#f0f0f0")


def _texto(valor):
    """Convierte a texto para el PDF; los vacíos (None) quedan en cadena vacía."""
    return "" if valor is None else str(valor)


def _estilos():
    """Estilos de texto que usa el documento."""
    base = getSampleStyleSheet()["Normal"]
    return {
        "taller":   ParagraphStyle("taller", parent=base,
                                   fontName="Helvetica-Bold", fontSize=15, leading=18),
        "lema":     ParagraphStyle("lema", parent=base,
                                   fontName="Helvetica-Oblique", fontSize=9,
                                   textColor=_GRIS),
        "contacto": ParagraphStyle("contacto", parent=base, fontSize=8,
                                   textColor=_GRIS, alignment=TA_RIGHT, leading=11),
        "titulo":   ParagraphStyle("titulo", parent=base,
                                   fontName="Helvetica-Bold", fontSize=13,
                                   alignment=TA_CENTER, spaceAfter=10),
        "seccion":  ParagraphStyle("seccion", parent=base,
                                   fontName="Helvetica-Bold", fontSize=10,
                                   spaceBefore=6, spaceAfter=4),
        "normal":   ParagraphStyle("normal", parent=base, fontSize=9.5, leading=13),
        "etiqueta": ParagraphStyle("etiqueta", parent=base, fontSize=7.5,
                                   textColor=_GRIS),
        "firma":    ParagraphStyle("firma", parent=base, fontSize=8,
                                   alignment=TA_CENTER),
    }


def generar_resguardo_pdf(datos):
    """
    Devuelve un BytesIO con el PDF del resguardo. 'datos' es el mismo diccionario
    que usa la plantilla (incidencia + cliente + vehículo + reparaciones).
    """
    buffer = io.BytesIO()
    documento = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="Resguardo de depósito",
    )
    e = _estilos()
    cuerpo = []

    # ---- Cabecera: taller a la izquierda, contacto a la derecha ----
    izquierda = [Paragraph(TALLER["nombre"], e["taller"])]
    if TALLER.get("lema"):
        izquierda.append(Paragraph(TALLER["lema"], e["lema"]))
    contacto = TALLER.get("direccion", "")
    if TALLER.get("telefono"):
        contacto += f'<br/>Tel. {TALLER["telefono"]}'
    if TALLER.get("email"):
        contacto += f' · {TALLER["email"]}'
    cabecera = Table([[izquierda, Paragraph(contacto, e["contacto"])]],
                     colWidths=[105 * mm, 69 * mm])
    cabecera.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    cuerpo.append(cabecera)
    cuerpo.append(HRFlowable(width="100%", thickness=1.2, color=_NARANJA,
                             spaceBefore=4, spaceAfter=8))

    # ---- Título con el número de resguardo (el id a 5 cifras) ----
    numero = f'{datos["id"]:05d}' if datos.get("id") else "____________"
    cuerpo.append(Paragraph(f"RESGUARDO DE DEPÓSITO N.º {numero}", e["titulo"]))

    # ---- Fechas ----
    fechas = Table([
        [Paragraph("Fecha de entrada", e["etiqueta"]),
         Paragraph("Entrega prevista", e["etiqueta"])],
        [Paragraph(fecha_es(datos.get("fecha_entrada")), e["normal"]),
         Paragraph(fecha_es(datos.get("fecha_entrega")), e["normal"])],
    ], colWidths=[87 * mm, 87 * mm])
    fechas.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, _GRIS_BORDE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, _GRIS_BORDE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    cuerpo.append(fechas)
    cuerpo.append(Spacer(1, 8))

    # ---- Cliente ----
    cuerpo.append(Paragraph("Cliente", e["seccion"]))
    linea = f'<b>{datos.get("nombre", "")}</b>'
    if datos.get("cif"):
        linea += f'&nbsp;&nbsp;·&nbsp;&nbsp;DNI/CIF: {datos["cif"]}'
    cuerpo.append(Paragraph(linea, e["normal"]))

    domicilio = datos.get("domicilio", "") or ""
    if datos.get("numero"):
        domicilio += f', {datos["numero"]}'
    cp_poblacion = " ".join(x for x in [datos.get("cp", ""),
                                        datos.get("poblacion", "")] if x)
    if cp_poblacion:
        domicilio = f'{domicilio} — {cp_poblacion}' if domicilio else cp_poblacion
    if domicilio:
        cuerpo.append(Paragraph(domicilio, e["normal"]))
    if datos.get("telefono"):
        cuerpo.append(Paragraph(f'Tel.: {datos["telefono"]}', e["normal"]))
    cuerpo.append(Spacer(1, 6))

    # ---- Vehículo (tabla etiqueta / valor) ----
    cuerpo.append(Paragraph("Vehículo", e["seccion"]))
    vehiculo = Table([
        ["Marca y modelo", _texto(datos.get("marca_modelo"))],
        ["Matrícula", _texto(datos.get("matricula"))],
        ["Kilómetros", _texto(datos.get("kilometros"))],
        ["Combustible", _texto(datos.get("combustible"))],
        ["Coste diario de estancia", TALLER.get("coste_diario", "")],
    ], colWidths=[55 * mm, 119 * mm])
    vehiculo.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_BORDE),
        ("BACKGROUND", (0, 0), (0, -1), _GRIS_FONDO),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    cuerpo.append(vehiculo)
    cuerpo.append(Spacer(1, 8))

    # ---- Trabajos a realizar ----
    cuerpo.append(Paragraph("Trabajos a realizar", e["seccion"]))
    reparaciones = datos.get("reparaciones") or []
    if reparaciones:
        for i, descripcion in enumerate(reparaciones, start=1):
            cuerpo.append(Paragraph(f"{i}.&nbsp;&nbsp;{descripcion}", e["normal"]))
    else:
        cuerpo.append(Paragraph("—", e["normal"]))
    cuerpo.append(Spacer(1, 18))

    # ---- Firmas ----
    firmas = Table([[
        Paragraph("___________________________<br/>Firma del cliente", e["firma"]),
        Paragraph("___________________________<br/>Por el taller", e["firma"]),
    ]], colWidths=[87 * mm, 87 * mm])
    firmas.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 12)]))
    cuerpo.append(firmas)

    documento.build(cuerpo)
    buffer.seek(0)
    return buffer
