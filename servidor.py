"""
Arranque en modo producción (para la demo o para el taller).

En desarrollo se usa 'python app.py', que levanta el servidor de pruebas de
Flask con recarga automática y modo debug. Ese servidor NO debe usarse de cara
al público: lo dice la propia documentación de Flask.

Para una puesta en marcha de verdad usamos 'waitress', un servidor WSGI
sencillo que funciona igual en Windows que en Linux. Se ejecuta con:

    python servidor.py

y se abre en el navegador http://127.0.0.1:8000 (o la IP del equipo dentro de
la red local del taller).
"""

from waitress import serve

# Importamos la app ya montada (al importar app.py se crea la base de datos si
# hace falta y se registran todas las rutas). El modo debug queda apagado: solo
# se activa cuando se arranca con 'python app.py'.
from app import app

if __name__ == "__main__":
    # host="0.0.0.0" permite entrar desde otros equipos de la red local (por
    # ejemplo, desde el ordenador del mostrador). El puerto 8000 es uno
    # cualquiera por encima de 1024; se puede cambiar si está ocupado.
    print("Servidor en marcha en http://127.0.0.1:8000  (Ctrl+C para parar)")
    serve(app, host="0.0.0.0", port=8000)
