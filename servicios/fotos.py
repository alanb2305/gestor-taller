"""
Lógica de ficheros de las fotos de los daños.

Separada de la ruta a propósito: aquí va todo lo que toca el sistema de
archivos (validar, guardar y borrar el fichero) y la ruta solo se ocupa de la
base de datos y de la respuesta web. La validación de tipo y tamaño se hace
AQUÍ, en el servidor, que es donde de verdad cuenta: el navegador puede saltarse
el accept="image/*" del formulario, así que nunca nos fiamos de él.
"""

import os
from uuid import uuid4

from config import DIR_FOTOS

# Extensiones de imagen que aceptamos. En minúsculas, porque el nombre que
# manda el navegador puede venir en mayúsculas (FOTO.JPG) y lo comparamos ya
# pasado a minúsculas.
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}

# Tamaño máximo por foto: 5 MB. Sobra para una foto de móvil y evita que se
# llene el disco con ficheros enormes.
MAX_BYTES = 5 * 1024 * 1024


def guardar(archivo):
    """
    Valida y guarda una foto subida. Devuelve el nombre con el que se ha
    guardado, o None si no pasa la validación (tipo o tamaño).

    'archivo' es un FileStorage de Werkzeug (cada elemento de request.files).
    """
    # Sin nombre de fichero no hay nada que guardar (input enviado en vacío).
    if not archivo or not archivo.filename:
        return None

    # Extensión en minúsculas, sacada del nombre original solo para decidir si
    # la aceptamos; el nombre con el que guardamos NO reutiliza el del usuario.
    _, extension = os.path.splitext(archivo.filename)
    extension = extension.lower()
    if extension not in EXTENSIONES:
        return None

    # Tamaño: nos vamos al final del fichero para saber cuántos bytes ocupa
    # (tell) y volvemos al principio para poder guardarlo entero después.
    archivo.seek(0, os.SEEK_END)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano == 0 or tamano > MAX_BYTES:
        return None

    # Nombre único y seguro: uuid4().hex da un nombre aleatorio (sin datos del
    # usuario) al que pegamos la extensión ya validada. Así dos fotos nunca
    # chocan y el nombre no puede traer caracteres raros ni rutas.
    nombre_archivo = uuid4().hex + extension
    archivo.save(os.path.join(DIR_FOTOS, nombre_archivo))
    return nombre_archivo


def borrar_archivo(nombre_archivo):
    """
    Borra el fichero de una foto de DIR_FOTOS si todavía existe. No falla si ya
    no está (por ejemplo, si se borró a mano): la fila de la base de datos es la
    que manda y el fichero solo la acompaña.
    """
    ruta = os.path.join(DIR_FOTOS, nombre_archivo)
    if os.path.exists(ruta):
        os.remove(ruta)
