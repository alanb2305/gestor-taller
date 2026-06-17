"""
Configuración general del proyecto.
Aquí guardamos en un solo sitio las rutas de los ficheros y los datos
fijos del taller, para no tenerlos repartidos por todo el código.
"""

import os

# Carpeta donde está este fichero = la raíz del proyecto.
# Usamos rutas relativas a esta carpeta para que el proyecto funcione
# en cualquier ordenador, sin rutas tipo "C:\Usuarios\...".
DIR_BASE = os.path.dirname(os.path.abspath(__file__))

# Rutas de la base de datos y del esquema SQL.
RUTA_BD      = os.path.join(DIR_BASE, "datos", "taller.db")
RUTA_ESQUEMA = os.path.join(DIR_BASE, "modelos", "esquema.sql")

# Carpeta donde se guardan las fotos de los daños subidas a cada ficha.
# Las imágenes viven aquí, fuera del código y de la base de datos (en la BD
# solo guardamos el nombre del archivo). La carpeta se crea al arrancar, en
# inicializar_bd(), igual que la de la base de datos.
DIR_FOTOS = os.path.join(DIR_BASE, "datos", "fotos")

# Clave que Flask usa para los mensajes flash y las sesiones.
# (Es un valor de ejemplo; en un despliegue real se pondría uno secreto.)
CLAVE_SECRETA = "cambia-esta-clave-en-produccion"

# Nombre del producto (la marca de la aplicación, no el del taller).
NOMBRE_APP = "GestorTaller"

# -----------------------------------------------------------------------------
# Datos del taller.
# La aplicación es genérica: NO tiene ningún taller concreto en el código.
# Los valores de abajo son de EJEMPLO; para usar la app en un taller real solo
# hay que cambiar este diccionario (no hay que tocar nada más). Estos datos se
# usan en las pantallas y en el resguardo en PDF.
# -----------------------------------------------------------------------------
TALLER = {
    "nombre":       "Taller de Ejemplo, S.L.",
    "lema":         "Servicio Integral del Automóvil",
    "direccion":    "Calle de Ejemplo, 0 · 00000 Ciudad",
    "telefono":     "000 000 000",
    "fax":          "000 000 000",
    "email":        "info@taller-ejemplo.example",
    "coste_diario": "20,00 €",
}
