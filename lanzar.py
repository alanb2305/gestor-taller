"""
Lanzador de la aplicación empaquetada (la versión .exe pensada para el tribunal).

A diferencia de 'servidor.py' (pensado para la red del taller, que escucha en
toda la red), este arranque es para una sola máquina: levanta el servidor en
local y abre el navegador por defecto en la página de la aplicación. Es el punto
de entrada que usa PyInstaller para generar 'GestorTaller.exe', de modo que el
tribunal solo tiene que hacer doble clic en el .exe y se encuentra la app ya en
marcha en el navegador.

Para cerrar la aplicación basta con cerrar la ventana de la consola.
"""

import threading
import webbrowser

from waitress import serve

# Al importar app.py se crea la base de datos (si hace falta) y se registran
# todas las rutas. El modo debug queda apagado.
from app import app

HOST = "127.0.0.1"   # solo este equipo: evita el aviso del cortafuegos de Windows
PUERTO = 8000
URL = f"http://{HOST}:{PUERTO}"


def abrir_navegador():
    """Abre el navegador por defecto en la página de la aplicación."""
    webbrowser.open(URL)


if __name__ == "__main__":
    print(f"GestorTaller en marcha en {URL}")
    print("Cierra esta ventana para detener la aplicación.")
    # Doy un margen a que el servidor esté escuchando y abro el navegador.
    threading.Timer(1.5, abrir_navegador).start()
    serve(app, host=HOST, port=PUERTO)
