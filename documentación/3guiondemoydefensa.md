# Guion 3 · Demo en vivo y defensa (lo que tienes que aprenderte)

> Este es el documento más importante de los tres. La rúbrica da un **20 %** a la
> presentación y la defensa, y dentro de eso lo que más pesa es que **respondas
> con seguridad a preguntas sobre tu propio código**. Aquí tienes: (1) el guion de
> la demo, (2) lo que debes saber sí o sí, (3) preguntas probables con respuesta,
> (4) cómo hablar de las partes en las que te ayudó la IA y (5) checklist final.
>
> Estúdialo hasta que puedas explicar cada punto **con tus palabras, sin leer**.
> Si una respuesta no la entiendes, abre el fichero del código que se menciona y
> míralo: todo lo de aquí está en tu repositorio.

---

## 1) Guion de la DEMO en vivo (4–5 minutos)

**Preparación antes de entrar (imprescindible):**
- Siembra datos de ejemplo para que haya historial y gráficas:
  `python datos_ejemplo.py` (crea 3 clientes con coches y fichas en varios
  estados). Hazlo **antes**, no en vivo.
- Ten el navegador abierto en `http://127.0.0.1:8000` (o el `.exe` ya arrancado) y
  el zoom del navegador subido para que se vea de lejos.
- Cierra pestañas y notificaciones. Ten a mano una **matrícula nueva** inventada
  válida (p. ej. `7777 KLM`) y una **ya existente** (`1234 BCD`, de los datos de
  ejemplo) para enseñar el autorrelleno.

**Recorrido (di en voz alta lo que haces y por qué aporta valor):**

1. **Inicio (15 s).** "Esta es la pantalla principal: accesos rápidos y un resumen
   con dos gráficas, fichas por estado y por mes, que se calculan en el servidor."
2. **Nueva ficha con matrícula NUEVA (90 s).** Entra en *Nueva ficha*. Escribe la
   matrícula nueva, marca y modelo, km, combustible. Rellena el cliente. Enseña que
   si pones un **DNI o una matrícula mal**, el formulario te **avisa al momento**
   (validación en el navegador) — "pero ojo, la validación de verdad está en el
   servidor". Añade dos **trabajos** con el botón +, sube una **foto** (se ve la
   miniatura) y pulsa **Generar resguardo**.
3. **Resguardo + PDF (45 s).** Muestra el resguardo en pantalla y pulsa **Descargar
   PDF**: "el PDF lo genera el servidor con ReportLab, en memoria, no se guarda
   ningún fichero". Abre el PDF un segundo.
4. **Autorrelleno con matrícula EXISTENTE (45 s).** *Nueva ficha* otra vez, escribe
   `1234 BCD` y sal del campo: "al ser una matrícula ya registrada, la app pide al
   servidor los datos del cliente y del coche y rellena el formulario sola". Esto
   suele gustar al tribunal.
5. **Historial y estados (40 s).** Ve a *Historial*, **busca** por matrícula o
   nombre, y a una ficha pásala de estado con el botón ("recepcionado → en
   reparación…"): "el estado siguiente lo decide el servidor".
6. **Agenda (20 s).** Enseña la agenda: entregas **vencidas, de hoy y próximas**.
7. **Datos / CSV (20 s, opcional).** Exporta el historial a CSV y ábrelo en Calc:
   "compatible con el Excel español; y se puede volver a importar".
8. **Cierre (10 s).** Vuelve al inicio. "Y todo esto se entrega como un `.exe` que
   el tribunal abre con doble clic, sin instalar Python."

**Plan B (tenlo preparado, da mucha tranquilidad):**
- Si el `.exe` falla, arranca el proyecto con `python servidor.py` (ténlo ya
  abierto en una terminal de reserva).
- Si se cae algo en vivo, ten **capturas o un vídeo corto** de cada paso en la
  presentación para seguir sin cortarte. La rúbrica perdona una demo "dubitativa",
  pero no quedarte en blanco.

---

## 2) Lo que tienes que saber SÍ o SÍ (con tus palabras)

### Arquitectura y organización
- **Está por capas.** `modelos/` accede a la base de datos (un módulo por tabla),
  `rutas/` son los controladores (reciben la petición y responden), `servicios/`
  tienen la lógica reutilizable (validaciones, PDF, CSV, fotos) y `templates/` son
  las vistas. Lo hice así para **separar responsabilidades**: si toco el PDF no
  rompo la base de datos, y cada cosa está en su sitio.
- **Blueprints.** Cada parte de la app (inicio, incidencias, clientes…) es un
  *blueprint* de Flask, que es su manera de **agrupar rutas** en módulos. Se
  registran todos en `app.py`. Sin esto tendría todas las rutas en un único fichero
  gigante.
- **Puntos de entrada.** `app.py` para desarrollar (con recarga y `debug`),
  `servidor.py` para producción con **Waitress** (sirve en la red local), y
  `lanzar.py` para el `.exe` (arranca en local y **abre el navegador** solo).

### Base de datos
- **SQLite**, un fichero (`datos/taller.db`). No necesita instalar un servidor de
  base de datos: perfecto para un taller con un equipo. Lo manejo con el módulo
  `sqlite3` de la **librería estándar** de Python.
- **Cinco tablas**: `clientes → vehiculos → incidencias → reparaciones/fotos`, con
  **claves foráneas**. La `matricula` es **UNIQUE** (identifica al coche). El
  `estado` tiene un **CHECK** (solo los cuatro válidos). Las reparaciones y fotos
  van con **ON DELETE CASCADE**: si borro una ficha, se borran sus líneas y fotos.
- Activo las claves foráneas con `PRAGMA foreign_keys = ON` (SQLite las trae
  **desactivadas** por compatibilidad). Y uso `row_factory = sqlite3.Row` para leer
  las columnas **por nombre** (`fila["nombre"]`) en vez de por posición.

### Seguridad y validación (esto da nota: domínalo)
- **Inyección SQL: la evito con consultas parametrizadas.** Nunca pego variables
  en el SQL; uso `?` y le paso los valores aparte, así la base de datos los trata
  como datos y no como código.
- **La validación que cuenta está en el servidor.** El JavaScript valida mientras
  escribes (comodidad), pero el navegador se puede saltar, así que **vuelvo a
  validar todo en el servidor** (`servicios/validaciones.py`) antes de guardar.
- **Validaciones propias:** la **letra del DNI/NIE** se comprueba con el algoritmo
  oficial (resto de dividir el número entre 23 → letra de una tabla); el NIE cambia
  su primera letra X/Y/Z por 0/1/2. La **matrícula** se valida con expresiones
  regulares para el formato actual (`1234BCD`) y el antiguo (`M1234AB`). También
  teléfono y código postal.
- **Transacciones.** Guardar una ficha toca varias tablas (cliente, vehículo,
  incidencia, reparaciones, fotos). Lo hago **todo en una transacción**: si algo
  falla, `rollback` y no se guarda nada a medias; si va bien, `commit`.
- **POST-Redirect-GET.** Después de guardar **redirijo** al resguardo en lugar de
  devolver el HTML directamente, para que si el usuario **recarga** no se cree una
  ficha duplicada.
- **Fotos / path traversal.** Las fotos se validan en el servidor (extensión y
  tamaño máximo 5 MB), se guardan con un **nombre aleatorio (UUID)** —no el del
  usuario— y se sirven con `send_from_directory`, que impide salirse de la carpeta
  de fotos (evita que alguien pida `../../algo`).

### Frontend
- **Bootstrap 5** para la maquetación responsive y **Bootstrap Icons** para los
  iconos, cargados por **CDN**. Mis estilos propios van en `static/css/estilos.css`.
- **Jinja2**: todas las plantillas **heredan** de `base.html` (cabecera, menú,
  pie) y rellenan bloques. Los datos del taller están disponibles en todas las
  plantillas con un **context processor**, para no pasarlos en cada página.
- **JavaScript propio** (sin framework): `validaciones.js` (avisos en vivo),
  `autorrelleno.js` (fetch a un endpoint que devuelve JSON), `trabajos.js` (añadir/
  quitar líneas), `fotos.js` (previsualización) y `graficos.js` (Chart.js).
- **Gráficas**: el navegador pide los datos a `/estadisticas`; el **servidor** los
  calcula con `COUNT ... GROUP BY` y devuelve JSON; **Chart.js** solo los pinta.

### PDF, CSV y empaquetado
- **PDF con ReportLab**: construyo el resguardo con *flowables* (párrafos y tablas)
  en un `BytesIO` (memoria) y lo mando con `send_file`. No se escribe ningún PDF en
  disco.
- **CSV con el módulo `csv`**: exporto e importo clientes, vehículos e historial.
  Uso separador `;` y codificación **UTF-8 con BOM** (`utf-8-sig`) para que se abra
  bien en el **Excel español** (acentos y Ñ correctos). Al importar **reutilizo las
  mismas validaciones** del formulario.
- **`.exe` con PyInstaller**: empaqueta Python, las librerías y los recursos
  (plantillas, CSS/JS, esquema SQL) en un solo ejecutable. En `config.py` detecto
  si voy "congelado" (`sys.frozen`) y separo los **recursos** (de solo lectura,
  dentro del `.exe`, en `sys._MEIPASS`) de los **datos** (base de datos y fotos,
  que se crean en una carpeta `datos/` junto al `.exe`, porque dentro del `.exe` no
  se puede escribir).

---

## 3) Preguntas probables del tribunal (con respuesta modelo)

> Respóndelas con tus palabras. Donde diga "(personaliza)", mete tu experiencia
> real para que suene a ti.

**¿Por qué Flask y no Django u otro?**
Porque para el tamaño del proyecto Flask es **ligero y suficiente**: me da el
enrutado, las plantillas Jinja2 y poco más, y el resto lo decido yo. Django traía
mucho de serie (su ORM, su panel de administración) que no necesitaba y me habría
costado más de aprender. Flask me dejó entender **qué hace cada parte**.

**¿Por qué SQLite y no MySQL/PostgreSQL?**
Porque es una app pensada para **un taller en un equipo**: SQLite es un fichero,
no hay que instalar ni administrar un servidor de base de datos, y aun así es
**transaccional (ACID)**. Si el día de mañana fueran varios puestos escribiendo a
la vez por red, migraría a PostgreSQL o MySQL, pero para este alcance sería
sobredimensionar.

**¿Por qué SQL directo y no un ORM como SQLAlchemy?**
Para **demostrar que sé SQL** y mantener el control y la transparencia de cada
consulta. Un ORM sería la evolución natural si el proyecto creciera; lo tengo
identificado como línea futura.

**¿Qué es un Blueprint?**
Es la forma que tiene Flask de **organizar las rutas en módulos**. Cada parte de
la app es un blueprint y los registro todos en `app.py`. Así no tengo un único
fichero con todas las rutas.

**¿Cómo evitas la inyección SQL?**
Con **consultas parametrizadas**: nunca concateno valores en la cadena SQL, uso
`?` y paso los datos por separado, de modo que la base de datos los interpreta como
datos, nunca como instrucciones.

**Si ya validas en JavaScript, ¿para qué validar otra vez en el servidor?**
Porque la validación del navegador **se puede saltar** (desactivando JS o enviando
la petición a mano). Es solo comodidad para el usuario. La que **garantiza** que
no entren datos malos es la del servidor, y por eso ahí valido **todo** otra vez.

**Explica cómo validas el DNI.**
Tomo los 8 números, los divido entre 23 y el **resto** me da la posición de la
letra en una tabla fija (`TRWAGMYFPDXBNJZSQVHLCKE`). Si la letra escrita coincide
con esa, el DNI es válido. El NIE es igual, pero antes cambio su primera letra
(X→0, Y→1, Z→2). El CIF solo lo valido de **formato** (su dígito de control tiene
varias reglas; lo dejé como mejora futura, y lo digo en la memoria).

**¿Qué pasa si al guardar una ficha falla algo a mitad?**
Como va todo en una **transacción**, hago `rollback` y **no se guarda nada**: ni el
cliente, ni el vehículo, ni la incidencia. Evito quedarme con datos a medias. Si
todo va bien, hago `commit`.

**¿Por qué rediriges después de guardar?**
Es el patrón **POST-Redirect-GET**. Si devolviera el HTML directamente, al
**recargar** la página el navegador reenviaría el formulario y se crearía una
ficha duplicada. Redirigiendo, al recargar solo se vuelve a ver el resguardo.

**¿Cómo funciona el autorrelleno por matrícula?**
Cuando escribes una matrícula y sales del campo, el JavaScript llama por `fetch` a
`/incidencias/matricula/<matricula>`. El servidor busca el vehículo y su cliente
con un **JOIN** y devuelve los datos en **JSON**. El JavaScript los pone en los
campos. Si la matrícula es nueva, responde "no encontrado" y no toca nada. Antes
**normalizo** la matrícula (mayúsculas, sin guiones ni espacios) para que
`1234-bcd` y `1234 BCD` se traten igual.

**¿Cómo generas el PDF?**
Con **ReportLab**. Monto el documento con bloques (párrafos y tablas), lo escribo
en un `BytesIO` (en **memoria**) y lo envío con `send_file`. No guardo el PDF en el
servidor; se genera cada vez a partir de los mismos datos que se ven en pantalla.

**¿Por qué el CSV con `;` y UTF-8 con BOM?**
Para que se abra correctamente en el **Excel en español**, que por defecto espera
el punto y coma como separador y necesita el BOM para mostrar bien acentos y Ñ.

**¿Cómo aseguras que las fotos no son un riesgo?**
Las valido en el servidor (solo JPG/PNG/WEBP y máximo 5 MB), las guardo con un
**nombre UUID** aleatorio (no el del usuario, que podría traer rutas o caracteres
raros) y las sirvo con `send_from_directory`, que **impide salir** de la carpeta de
fotos. Así evito el *path traversal*.

**¿Cómo se ejecuta sin instalar Python? / ¿Cómo hiciste el `.exe`?**
Con **PyInstaller**, que empaqueta el intérprete, las librerías y los recursos en
un único ejecutable. El reto fue que, dentro del `.exe`, los recursos van en una
carpeta temporal de **solo lectura**; por eso en `config.py` distingo esa carpeta
de la de **datos** (base de datos y fotos), que se crea **junto al `.exe`** para
poder escribir. Al abrirlo, `lanzar.py` levanta el servidor y abre el navegador.

**¿Por qué Waitress y no el servidor de Flask?**
El servidor que trae Flask es **solo para desarrollo** (lo avisa él mismo) y no
está pensado para uso real. **Waitress** es un servidor WSGI de producción, va
igual en Windows que en Linux y no necesita configuración complicada.

**¿Esto aguanta varios usuarios a la vez?**
Para un taller pequeño, sí: las peticiones son rápidas y SQLite **serializa** las
escrituras. Si hubiera muchos puestos escribiendo simultáneamente por red, el
siguiente paso sería **PostgreSQL**. Está en mis líneas futuras.

**¿Tiene control de acceso / login?**
No, porque está pensada para uso **interno** en la red del taller. Lo tengo como
línea futura, junto con protección **CSRF** en los formularios, que también
menciono en la memoria como mejora de seguridad.

**¿Qué es lo que más te costó? (personaliza)**
(Cuenta un problema real: p. ej. que el `.exe` encontrara las plantillas, o cuadrar
la maquetación del PDF, o la lógica del autorrelleno sin pisar los datos de la
visita actual.) Explica **cómo lo resolviste**: eso es lo que valora el tribunal.

**¿Qué mejorarías si tuvieras más tiempo?**
Login con roles, protección CSRF, **paginación** del historial, **facturación/
precios** de las reparaciones, validación completa del dígito de control del CIF,
y **pruebas automáticas** con `pytest` (ahora las pruebas son manuales).

**¿Usaste IA? ¿En qué?** → ver sección 4.

---

## 4) Cómo hablar del uso de IA (con naturalidad y honestidad)

Lo declaras en la memoria y en la presentación, así que si te preguntan, respondes
tranquilo. Mensaje:

> "Usé un asistente de IA como **herramienta de apoyo**, igual que la documentación
> oficial o Stack Overflow, en tres cosas concretas: la **hoja de estilos CSS**, la
> **plantilla del PDF** del resguardo y el **empaquetado en `.exe`**. Todo eso lo
> **revisé y entendí**, y puedo explicarlo. El análisis, el diseño de la base de
> datos y la lógica de la aplicación los trabajé yo."

**Por eso tienes que entender de verdad esas tres partes**, que son justo donde te
pueden apretar:
- **CSS:** sé explicar la paleta (acento naranja `#e07b00`), que uso Bootstrap para
  la rejilla y mis estilos para la "hoja" del resguardo, y cómo consigo que al
  imprimir no salgan botones (clase `no-imprimir`).
- **PDF (ReportLab):** sé explicar que uso *flowables* (párrafos y tablas), que se
  genera en memoria y que reutiliza los mismos datos que la vista en pantalla.
- **`.exe` (PyInstaller):** sé explicar lo de los recursos de solo lectura vs. la
  carpeta de datos escribible (lo de `config.py` y `sys._MEIPASS`).

Si dominas esas tres, la declaración de IA **suma madurez** en vez de restar.

---

## 5) Glosario rápido (que no te pillen con un término)

- **WSGI:** el estándar de Python para que un servidor web hable con una app
  (Flask y Waitress lo cumplen).
- **Framework / microframework:** Flask te da lo básico (rutas, plantillas) y tú
  pones el resto.
- **Blueprint:** módulo de rutas en Flask.
- **CRUD:** Crear, Leer, Actualizar, Borrar (lo que hace la gestión de clientes y
  vehículos).
- **Clave foránea (FK):** columna que apunta a la clave primaria de otra tabla
  (relaciona las tablas).
- **Transacción / ACID:** conjunto de operaciones que se confirman juntas
  (`commit`) o se deshacen juntas (`rollback`).
- **Inyección SQL:** ataque que mete código en una consulta; se evita con
  parámetros.
- **Path traversal:** truco para salir de una carpeta permitida (p. ej. `../`);
  se evita sirviendo ficheros de forma controlada.
- **AJAX / fetch:** pedir datos al servidor sin recargar la página.
- **JSON:** formato de texto para intercambiar datos (lo que devuelve el endpoint
  del autorrelleno y el de las gráficas).
- **CDN:** servidor desde el que cargo Bootstrap y Chart.js sin tenerlos en mi
  proyecto.
- **Jinja2 / herencia de plantillas:** motor de plantillas; `base.html` define la
  estructura y las demás la heredan.
- **PRAGMA foreign_keys:** orden de SQLite para activar el respeto de las FK.

---

## 6) Errores típicos que debes evitar en la defensa

- **Leer las diapositivas.** Mortal para la nota. Mira al tribunal y usa las notas
  del orador solo de apoyo.
- **Pasarte de tiempo.** Ensaya con cronómetro al menos **dos veces** enteras.
- **Demo sin red de seguridad.** Ten el plan B (proyecto arrancado aparte +
  capturas).
- **Decir "esto lo hizo la IA" sin saber explicarlo.** Si lo declaras, domínalo.
- **Inventar.** Si no sabes algo, di "eso no lo implementé, pero lo haría así…".
  El tribunal valora más la honestidad y el criterio que un farol.

---

## 7) Checklist final (24 h antes)

- [ ] `python datos_ejemplo.py` ejecutado: hay historial, estados variados y
      gráficas.
- [ ] `.exe` probado en un equipo **sin Python** (o, en su defecto,
      `python servidor.py` listo en una terminal).
- [ ] Presentación exportada a **.odp, .pptx y PDF** en un USB.
- [ ] Capturas/vídeo de respaldo de cada paso de la demo.
- [ ] Matrícula nueva y matrícula existente (`1234 BCD`) anotadas para la demo.
- [ ] Ensayo completo cronometrado ×2, dentro del tiempo.
- [ ] Repaso de la sección 3 (preguntas) en voz alta.
- [ ] Datos de la portada (nombre, tutor, centro) correctos en memoria y
      presentación.

---

## 8) (Opcional) Prompt para que el asistente te examine

> Pega esto en el asistente para practicar la defensa:

"Eres un tribunal de TFG de un ciclo de DAM, exigente pero justo. Te paso el
resumen de mi proyecto (GestorTaller: app web Flask + SQLite para gestionar un
taller, con resguardo en PDF, autorrelleno por matrícula, historial, agenda,
gráficas, CSV y empaquetado `.exe`; arquitectura por capas modelos/rutas/servicios;
seguridad con SQL parametrizado, validación en servidor, transacciones y
prevención de path traversal). **Hazme una pregunta cada vez**, espera mi
respuesta, puntúala del 1 al 5 y dime cómo mejorarla antes de la siguiente.
Empieza por preguntas fáciles y sube la dificultad. Incluye alguna pregunta
incómoda sobre las partes en las que usé IA (CSS, plantilla del PDF y `.exe`)."
