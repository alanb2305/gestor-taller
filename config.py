"""
Configuración del proyecto: rutas de los ficheros y datos del taller en un
solo sitio, para no tenerlos repartidos por el código.
"""

import os

# Raíz del proyecto. Trabajo con rutas relativas a esta carpeta para que
# funcione en cualquier ordenador (sin rutas tipo "C:\Usuarios\...").
DIR_BASE = os.path.dirname(os.path.abspath(__file__))

# Base de datos y esquema SQL.
RUTA_BD      = os.path.join(DIR_BASE, "datos", "taller.db")
RUTA_ESQUEMA = os.path.join(DIR_BASE, "modelos", "esquema.sql")

# Carpeta de las fotos de los daños. En la base de datos solo guardo el nombre
# del archivo; la imagen se guarda aquí. La carpeta se crea en inicializar_bd().
DIR_FOTOS = os.path.join(DIR_BASE, "datos", "fotos")

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
