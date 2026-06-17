"""
Parte de ficheros de las fotos de los daños (validar, guardar y borrar el
archivo). La ruta solo se ocupa de la base de datos. La validación de tipo y
tamaño se hace aquí, en el servidor: el navegador puede saltarse el
accept="image/*" del formulario, así que no me fío de él.
"""

import os
from uuid import uuid4

from config import DIR_FOTOS

# Extensiones de imagen que aceptamos (en minúsculas, porque el nombre puede
# venir como FOTO.JPG y lo comparo ya en minúsculas).
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}

# Tamaño máximo por foto: 5 MB (sobra para una foto de móvil).
MAX_BYTES = 5 * 1024 * 1024


def guardar(archivo):
    """
    Valida y guarda una foto subida. Devuelve el nombre con el que se ha guardado,
    o None si no pasa la validación (tipo o tamaño). 'archivo' es un FileStorage
    de Werkzeug (cada elemento de request.files).
    """
    # Sin nombre de fichero no hay nada que guardar.
    if not archivo or not archivo.filename:
        return None

    # Extensión (en minúsculas) solo para decidir si la aceptamos; el nombre con
    # el que guardo NO reutiliza el del usuario.
    _, extension = os.path.splitext(archivo.filename)
    extension = extension.lower()
    if extension not in EXTENSIONES:
        return None

    # Tamaño: voy al final del fichero para ver cuántos bytes ocupa (tell) y
    # vuelvo al principio para poder guardarlo entero.
    archivo.seek(0, os.SEEK_END)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano == 0 or tamano > MAX_BYTES:
        return None

    # Nombre único: uuid4().hex da un nombre aleatorio al que pego la extensión
    # ya validada. Así dos fotos no chocan y el nombre no trae caracteres raros.
    nombre_archivo = uuid4().hex + extension
    archivo.save(os.path.join(DIR_FOTOS, nombre_archivo))
    return nombre_archivo


def borrar_archivo(nombre_archivo):
    """
    Borra el fichero de una foto si todavía existe. No falla si ya no está: manda
    la fila de la base de datos y el fichero solo la acompaña.
    """
    ruta = os.path.join(DIR_FOTOS, nombre_archivo)
    if os.path.exists(ruta):
        os.remove(ruta)
