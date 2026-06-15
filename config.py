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

# Clave que Flask usa para los mensajes flash y las sesiones.
# (Es un valor de ejemplo; en un despliegue real se pondría uno secreto.)
CLAVE_SECRETA = "cambia-esta-clave-en-produccion"

# Nombre del producto (la marca de la aplicación, no el del taller).
NOMBRE_APP = "GestorTaller"

# -----------------------------------------------------------------------------
# Datos del taller.
# La aplicación es genérica: NO tiene ningún nombre de taller en el código.
# Para adaptarla a otro taller solo hay que cambiar este diccionario.
# Estos valores se usarán en las pantallas y en el resguardo en PDF.
# -----------------------------------------------------------------------------
TALLER = {
    "nombre":       "TALLERES LUJOSMAR, S.L.",
    "lema":         "Servicio Integral del Automóvil",
    "direccion":    "C.º del Pilón, 17-19 · 50011 Zaragoza",
    "telefono":     "976 330 695",
    "fax":          "976 906 058",
    "email":        "lujosmar@tallereslujosmar.com",
    "coste_diario": "20,00 €",
}
