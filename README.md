# GestorTaller

Aplicación web para la gestión de un taller de automóviles: clientes,
vehículos, órdenes de trabajo (incidencias) y generación del resguardo
de depósito en PDF.

Proyecto de Trabajo de Fin de Grado (DAM). La aplicación es **genérica**:
para adaptarla a un taller concreto solo hay que cambiar los datos del
fichero `config.py`.

> Estado: en desarrollo.

## Tecnologías
- Python + Flask
- Base de datos SQLite
- HTML, CSS y JavaScript con Bootstrap
- Chart.js para los gráficos
- ReportLab para el PDF

## Cómo ejecutar

1. (Opcional) Crear un entorno virtual:

       python -m venv venv
       venv\Scripts\activate        # Windows
       source venv/bin/activate     # Linux / Mac

2. Instalar las dependencias:

       pip install -r requirements.txt

3. Arrancar la aplicación:

       python app.py

4. Abrir en el navegador: http://127.0.0.1:5000

La base de datos (`datos/taller.db`) se crea sola la primera vez.

## Estructura del proyecto

    gestor_taller/
    ├── app.py          punto de entrada
    ├── config.py       configuración y datos del taller
    ├── modelos/        acceso a la base de datos
    ├── rutas/          las pantallas (rutas de Flask)
    ├── servicios/      generación de PDF y validaciones
    ├── templates/      plantillas HTML
    ├── static/         CSS, JS e imágenes
    └── datos/          base de datos SQLite
