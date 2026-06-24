# GestorTaller

**Aplicación web de uso local para gestionar un taller de automóviles.** Sustituye al
papel y a las libretas: lleva los clientes, los coches y las entradas al taller, y genera
el **resguardo de depósito** —el justificante que se entrega al cliente cuando deja el
coche— listo para imprimir o descargar en PDF.

Proyecto de Trabajo de Fin de Grado del ciclo de **Desarrollo de Aplicaciones
Multiplataforma (DAM)**.

## El problema que resuelve

Muchos talleres pequeños se gestionan con papel: las fichas se pierden, hay que reescribir
los datos del mismo cliente una y otra vez y no hay forma cómoda de saber qué coches están
pendientes de entregar. GestorTaller ordena justo eso, y guarda un historial consultable de
todo lo que ha pasado por el taller.

## Qué hace

- Da de alta la **ficha de cada coche** (la orden de trabajo) y genera su **resguardo en PDF**.
- **Autorrellena** los datos del cliente y del vehículo al escribir una matrícula ya conocida.
- Guarda el **historial** con buscador y controla el **estado** de cada reparación
  (recepcionado → en reparación → terminado → entregado).
- **Agenda** de entregas, agrupadas en vencidas, de hoy y próximas.
- Panel de inicio con **gráficas** de resumen e **importación/exportación en CSV**.
- Es **genérica**: para adaptarla a otro taller solo se cambia el fichero `config.py`.

## Tecnologías

Python + **Flask** · base de datos **SQLite** · HTML, CSS y JavaScript con **Bootstrap** ·
**Chart.js** para las gráficas · **ReportLab** para el PDF · **Waitress** como servidor ·
**PyInstaller** para el ejecutable.

## Cómo ejecutarlo

Requisito: **Python 3.10 o superior**.

```
pip install -r requirements.txt
python app.py
```

Se abre en `http://127.0.0.1:5000`. La base de datos se crea sola la primera vez.

Para la demostración conviene sembrar datos de prueba y usar el servidor de producción:

```
python datos_ejemplo.py     # rellena clientes, coches y fichas de ejemplo
python servidor.py          # http://127.0.0.1:8000
```

Para que el tribunal lo pruebe **sin instalar nada**, el proyecto se empaqueta en un único
ejecutable con `pyinstaller gestor_taller.spec`: el `.exe` (en `dist\GestorTaller.exe`)
arranca con doble clic y abre el navegador solo.

## Estructura del proyecto

```
modelos/     acceso a datos: un módulo por tabla + esquema.sql
rutas/       controladores (Blueprints de Flask)
servicios/   validaciones, generación de PDF, CSV y fotos
templates/   vistas (plantillas Jinja2)
static/      CSS y JavaScript
config.py    datos del taller (lo único que se cambia para otro taller)
```

La aplicación está organizada **por capas** para que sea fácil de entender y mantener: las
rutas reciben la petición, los servicios contienen la lógica y los modelos hablan con la
base de datos.

---

Autor: **Alain Blanquies Marco** · DAM · CESTE Centro Universitario
