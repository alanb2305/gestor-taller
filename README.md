# GestorTaller

Aplicación web para la gestión de un taller de automóviles: clientes,
vehículos, órdenes de trabajo (incidencias) y generación del resguardo de
depósito en PDF, con un panel de gráficas y exportación/importación en CSV.

Proyecto de Trabajo de Fin de Grado (DAM). La aplicación es **genérica**: para
adaptarla a un taller concreto solo hay que cambiar los datos del fichero
`config.py` (no hay que tocar nada más).

## Tecnologías

- Python + Flask
- Base de datos SQLite
- HTML, CSS y JavaScript con Bootstrap
- Chart.js para las gráficas
- ReportLab para el PDF
- Waitress como servidor en producción

## Requisitos

- Python 3.10 o superior.

## Instalación

1. Crear un entorno virtual (recomendado):

       python -m venv venv
       venv\Scripts\activate          # Windows
       source venv/bin/activate       # Linux / Mac

2. Instalar las dependencias:

       pip install -r requirements.txt

## Ejecución

**En desarrollo** (con recarga automática y modo depuración):

       python app.py

Abre en el navegador: http://127.0.0.1:5000

**En producción o para la demo** (servidor Waitress, sin modo depuración):

       python servidor.py

Abre en el navegador: http://127.0.0.1:8000

La base de datos (`datos/taller.db`) se crea sola la primera vez.

## Datos de ejemplo (opcional)

Para rellenar la base con clientes, coches y fichas de prueba y poder enseñar
el autorrelleno, el historial, los estados y las gráficas:

       python datos_ejemplo.py

Solo siembra si la base está vacía, así no se duplican los datos.

## Estructura del proyecto

    gestor_taller/
    ├── app.py            punto de entrada (desarrollo)
    ├── servidor.py       arranque en producción (Waitress)
    ├── config.py         configuración y datos del taller
    ├── datos_ejemplo.py  siembra datos de prueba
    ├── requirements.txt
    ├── modelos/          acceso a datos (conexion, cliente, vehiculo,
    │                     incidencia, reparacion, esquema.sql)
    ├── rutas/            las pantallas (principal, incidencias, clientes,
    │                     vehiculos, datos)
    ├── servicios/        validaciones, generación de PDF, import/export CSV
    ├── templates/        plantillas HTML
    ├── static/           CSS y JavaScript
    └── datos/            base de datos SQLite (se crea sola)

## Despliegue en la nube (opcional)

La aplicación es una app WSGI estándar de Flask (el objeto `app` de `app.py`),
así que puede subirse a un alojamiento gratuito como **PythonAnywhere** o
**Render**. A grandes rasgos: subir el código, crear allí un entorno virtual e
instalar `requirements.txt`, y configurar el servidor de la plataforma para que
importe `app` desde `app.py` (en PythonAnywhere, en su fichero WSGI; en Render,
con un comando de arranque tipo `waitress-serve --listen=*:$PORT app:app`).
Como los detalles de cada plataforma cambian, conviene seguir su guía oficial
actual. Para la defensa, muchas veces basta con ejecutarlo en local con
`python servidor.py`.

## Notas de seguridad

La `CLAVE_SECRETA` de `config.py` es de ejemplo. Para un despliegue público de
verdad conviene poner una clave secreta propia (idealmente desde una variable
de entorno) y añadir protección CSRF a los formularios. Para uso dentro de la
red local del taller no es crítico.
