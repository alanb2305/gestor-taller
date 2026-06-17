"""
Configuración del proyecto: rutas de los ficheros y datos del taller en un
solo sitio, para no tenerlos repartidos por el código.
"""

import os
import sys

# La app puede arrancar de dos maneras y las rutas cambian según el caso:
#   - normal, con Python (python app.py)
#   - como .exe hecho con PyInstaller, para que el tribunal solo tenga que hacer
#     doble clic sin instalar nada
# Dentro del .exe, PyInstaller descomprime las plantillas, el CSS/JS y el
# esquema.sql en una carpeta temporal (sys._MEIPASS) de solo lectura. La base de
# datos y las fotos NO pueden ir ahí (se perderían al cerrar), así que esas van
# junto al .exe. Por eso distingo dos carpetas base.
if getattr(sys, "frozen", False):
    # Ejecutándose desde el .exe.
    DIR_RECURSOS = sys._MEIPASS                      # archivos del programa (solo lectura)
    DIR_DATOS    = os.path.dirname(sys.executable)   # junto al .exe (se puede escribir)
else:
    # Ejecutándose normal, con el intérprete de Python.
    DIR_RECURSOS = os.path.dirname(os.path.abspath(__file__))
    DIR_DATOS    = DIR_RECURSOS

# Mantengo DIR_BASE para el resto del código; apunta a los recursos del programa.
DIR_BASE = DIR_RECURSOS

# Base de datos y esquema SQL. La base de datos se escribe (va en DIR_DATOS); el
# esquema viene con el programa (va en DIR_RECURSOS). Con rutas relativas a estas
# carpetas la app funciona en cualquier ordenador (sin rutas tipo "C:\Usuarios\...").
RUTA_BD      = os.path.join(DIR_DATOS, "datos", "taller.db")
RUTA_ESQUEMA = os.path.join(DIR_RECURSOS, "modelos", "esquema.sql")

# Carpeta de las fotos de los daños. En la base de datos solo guardo el nombre
# del archivo; la imagen se guarda aquí. La carpeta se crea en inicializar_bd().
# Va con la base de datos (se escribe), no con los recursos del programa.
DIR_FOTOS = os.path.join(DIR_DATOS, "datos", "fotos")

# Clave de Flask para los flash y las sesiones (de ejemplo; en producción
# habría que poner una secreta de verdad).
CLAVE_SECRETA = "cambia-esta-clave-en-produccion"

# Nombre de la aplicación.
NOMBRE_APP = "GestorTaller"

# -----------------------------------------------------------------------------
# Datos del taller. La app es genérica: estos valores son de EJEMPLO y para
# usarla en un taller real solo hay que cambiar este diccionario. Se usan en
# las pantallas y en el resguardo.
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
