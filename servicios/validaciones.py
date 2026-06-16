"""
Validaciones de los datos del formulario.

Las reunimos en un único sitio (este servicio) para reutilizarlas y para
tener "una sola verdad": las mismas reglas valen para el alta de hoy y para
cuando guardemos en la base de datos.

Importante: estas son las validaciones del SERVIDOR. Hay otras parecidas en
JavaScript (static/js/validaciones.js) que avisan al usuario mientras escribe,
pero esas son solo comodidad. El navegador se puede saltar, así que la
comprobación seria se hace siempre aquí.
"""

import re
from datetime import date


# Letras de control del DNI/NIE. La posición se calcula con el resto de
# dividir el número entre 23 (es el algoritmo oficial).
_LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"


# ---------------------------------------------------------------------------
# Normalización (no es una validación, pero va de la mano de la matrícula).
# ---------------------------------------------------------------------------

def normalizar_matricula(texto):
    """
    Deja una matrícula en forma canónica: en mayúsculas y sin guiones ni
    espacios, para que '1234-bcd' o '1234 BCD' se traten como la misma.
    La usan el formulario, la gestión de vehículos, el autorrelleno y la
    importación de CSV; así la normalización está en un único sitio y no
    repetida por todo el código.
    """
    return (texto or "").upper().replace("-", "").replace(" ", "")


# ---------------------------------------------------------------------------
# Validaciones de cada campo por separado. Devuelven True/False.
# Si un campo es opcional y está vacío, lo damos por bueno (True): la
# obligatoriedad se comprueba aparte, en validar_incidencia().
# ---------------------------------------------------------------------------

def validar_fecha(texto):
    """Comprueba que sea una fecha real en formato AAAA-MM-DD."""
    try:
        date.fromisoformat(texto)
        return True
    except (ValueError, TypeError):
        return False


def fecha_entrega_coherente(entrada, entrega):
    """La entrega no puede ser anterior a la entrada."""
    if not (validar_fecha(entrada) and validar_fecha(entrega)):
        return False
    return date.fromisoformat(entrega) >= date.fromisoformat(entrada)


def validar_cp(texto):
    """Código postal español: 5 dígitos, entre 01000 y 52999."""
    if not texto:
        return True
    return bool(re.fullmatch(r"\d{5}", texto)) and 1000 <= int(texto) <= 52999


def validar_telefono(texto):
    """Teléfono español: 9 dígitos que empiezan por 6, 7, 8 o 9."""
    if not texto:
        return True
    limpio = texto.replace(" ", "")
    return bool(re.fullmatch(r"[6789]\d{8}", limpio))


def validar_matricula(texto):
    """
    Matrícula española en sus dos formatos:
      - Actual (desde 2000): 4 números + 3 letras, sin vocales ni Ñ ni Q.
        Ejemplo: 1234BCD
      - Antigua: 1 o 2 letras de provincia + 4 números + 1 o 2 letras.
        Ejemplo: TE1234A, M1234AB
    """
    if not texto:
        return True
    t = normalizar_matricula(texto)
    nueva   = re.fullmatch(r"\d{4}[BCDFGHJKLMNPRSTVWXYZ]{3}", t)
    antigua = re.fullmatch(r"[A-Z]{1,2}\d{4}[A-Z]{1,2}", t)
    return bool(nueva or antigua)


def validar_kilometros(texto):
    """Kilómetros: solo dígitos (sin puntos ni comas)."""
    if not texto:
        return True
    return texto.isdigit()


def validar_documento(texto):
    """
    El campo admite tres cosas distintas, así que probamos por orden:
      - DNI -> validamos la letra de control.
      - NIE -> igual, pero la primera letra (X/Y/Z) cuenta como 0/1/2.
      - CIF -> validamos solo el formato. El dígito de control del CIF tiene
               varias reglas según el tipo de empresa, así que la comprobación
               completa la dejamos como mejora futura.
    Si está vacío lo damos por bueno (es un campo opcional).
    """
    if not texto:
        return True
    t = texto.upper().replace("-", "").replace(" ", "")

    if re.fullmatch(r"\d{8}[A-Z]", t):                       # DNI
        return _letra_dni_correcta(t)
    if re.fullmatch(r"[XYZ]\d{7}[A-Z]", t):                  # NIE
        return _letra_nie_correcta(t)
    if re.fullmatch(r"[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]", t): # CIF (solo formato)
        return True
    return False


def _letra_dni_correcta(dni):
    numero = int(dni[:8])
    return dni[8] == _LETRAS_DNI[numero % 23]


def _letra_nie_correcta(nie):
    # X=0, Y=1, Z=2: sustituimos esa primera letra y validamos como un DNI.
    primera = {"X": "0", "Y": "1", "Z": "2"}[nie[0]]
    numero = int(primera + nie[1:8])
    return nie[8] == _LETRAS_DNI[numero % 23]


# ---------------------------------------------------------------------------
# Validación del formulario completo.
# Recibe el diccionario de datos y devuelve otro con los errores:
#     { "nombre_del_campo": "mensaje para el usuario", ... }
# Si el diccionario que devuelve está vacío, es que no hay errores.
# ---------------------------------------------------------------------------

# Campos obligatorios y el mensaje que se enseña si faltan.
_OBLIGATORIOS = {
    "fecha_entrada": "La fecha de entrada es obligatoria.",
    "fecha_entrega": "La fecha de entrega es obligatoria.",
    "nombre":        "El nombre del cliente es obligatorio.",
    "marca_modelo":  "La marca y el modelo son obligatorios.",
    "matricula":     "La matrícula es obligatoria.",
}


def validar_incidencia(datos):
    errores = {}

    # 1) Obligatorios: que no estén vacíos.
    for campo, mensaje in _OBLIGATORIOS.items():
        if not datos.get(campo, "").strip():
            errores[campo] = mensaje

    # 2) Formato de las fechas (solo si tienen algo escrito).
    if datos.get("fecha_entrada") and not validar_fecha(datos["fecha_entrada"]):
        errores["fecha_entrada"] = "La fecha de entrada no es válida."
    if datos.get("fecha_entrega") and not validar_fecha(datos["fecha_entrega"]):
        errores["fecha_entrega"] = "La fecha de entrega no es válida."

    # 3) Coherencia entre fechas (solo si las dos son válidas y no hay ya error).
    if ("fecha_entrada" not in errores and "fecha_entrega" not in errores
            and datos.get("fecha_entrada") and datos.get("fecha_entrega")):
        if not fecha_entrega_coherente(datos["fecha_entrada"], datos["fecha_entrega"]):
            errores["fecha_entrega"] = "La entrega no puede ser anterior a la entrada."

    # 4) Formato del resto de campos.
    if not validar_documento(datos.get("cif", "")):
        errores["cif"] = "El DNI/NIF/CIF no es válido."
    if not validar_telefono(datos.get("telefono", "")):
        errores["telefono"] = "El teléfono debe tener 9 dígitos y empezar por 6, 7, 8 o 9."
    if not validar_cp(datos.get("cp", "")):
        errores["cp"] = "El código postal debe tener 5 dígitos."
    if datos.get("matricula") and not validar_matricula(datos["matricula"]):
        errores["matricula"] = "La matrícula no tiene un formato español válido."
    if not validar_kilometros(datos.get("kilometros", "")):
        errores["kilometros"] = "Los kilómetros deben ser solo números."

    return errores


# ---------------------------------------------------------------------------
# Validación de cliente y de vehículo por separado (para la pantalla de
# gestión: alta y edición). Mismas reglas de formato que la ficha; devuelven
# un diccionario {campo: mensaje}, igual que validar_incidencia().
# ---------------------------------------------------------------------------

def validar_cliente(datos):
    errores = {}
    if not datos.get("nombre", "").strip():
        errores["nombre"] = "El nombre es obligatorio."
    if not validar_documento(datos.get("cif", "")):
        errores["cif"] = "El DNI/NIF/CIF no es válido."
    if not validar_telefono(datos.get("telefono", "")):
        errores["telefono"] = "El teléfono debe tener 9 dígitos y empezar por 6, 7, 8 o 9."
    if not validar_cp(datos.get("cp", "")):
        errores["cp"] = "El código postal debe tener 5 dígitos."
    return errores


def validar_vehiculo(datos):
    # Solo el formato. Que la matrícula no esté repetida y que el cliente
    # exista se comprueban en la ruta, porque dependen de la base de datos.
    errores = {}
    if not datos.get("matricula", "").strip():
        errores["matricula"] = "La matrícula es obligatoria."
    elif not validar_matricula(datos["matricula"]):
        errores["matricula"] = "La matrícula no tiene un formato español válido."
    if not datos.get("marca_modelo", "").strip():
        errores["marca_modelo"] = "La marca y el modelo son obligatorios."
    return errores
