"""
Arranque en modo producción (para la demo o para el taller).

En desarrollo uso 'python app.py', que levanta el servidor de pruebas de Flask
con recarga automática. Ese servidor no conviene usarlo de cara al público, así
que para una puesta en marcha de verdad uso 'waitress' (un servidor WSGI que va
igual en Windows que en Linux):

    python servidor.py   ->   http://127.0.0.1:8000
"""

from waitress import serve

# Al importar app.py ya se crea la base de datos (si hace falta) y se registran
# todas las rutas. Aquí el modo debug queda apagado.
from app import app

if __name__ == "__main__":
    # host="0.0.0.0" permite entrar desde otros equipos de la red local (p. ej.
    # el ordenador del mostrador). El puerto 8000 se puede cambiar si está pillado.
    print("Servidor en marcha en http://127.0.0.1:8000  (Ctrl+C para parar)")
    serve(app, host="0.0.0.0", port=8000)
