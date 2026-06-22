# Guion 1 · Prompt para redactar la MEMORIA del TFG

> **Cómo usar este fichero.** Es un *prompt* preparado para pegárselo a un
> asistente (Claude). Pero la memoria la firmas tú: pásala siempre por tu propia
> revisión, cambia lo que no suene a como tú escribes y rellena los datos
> personales (nombre, centro, tutor, fechas…). Lo que el tribunal valora es que
> sepas defender cada frase. Si no entiendes algo de lo que sale, **no lo dejes**:
> míralo en el Guion 3 (defensa) hasta que lo puedas explicar de viva voz.
>
> **Importante:** este fichero y la carpeta `guiones-tfg/` son material de
> trabajo. No los entregues ni los subas a la rama que vea el tribunal.

---

## Cómo trabajar la memoria por partes

Una memoria es larga; si la pides toda de golpe sale genérica. Pídela **capítulo
a capítulo** con este guion, revisando cada uno antes de seguir. Orden sugerido:

1. Portada + índice + resumen/abstract
2. Introducción y objetivos
3. Análisis de requisitos
4. Diseño (arquitectura, base de datos, UML, interfaz)
5. Implementación (decisiones técnicas por módulos)
6. Pruebas
7. Despliegue y empaquetado
8. Manual de usuario
9. Manual técnico (instalación/configuración)
10. Conclusiones y líneas futuras
11. Bibliografía

---

## EL PROMPT (a partir de aquí, pégaselo al asistente)

Actúa como mi copiloto de redacción técnica. Vamos a escribir, capítulo a
capítulo, la **memoria** de mi Trabajo de Fin de Grado del ciclo de **Desarrollo
de Aplicaciones Multiplataforma (DAM)**. Yo soy un estudiante de **segundo año**.
No escribas toda la memoria de una vez: te iré pidiendo los capítulos por orden y
me detendré a revisar cada uno.

### 1) Contexto del proyecto (datos reales, úsalos como única fuente de verdad)

**Nombre:** GestorTaller.

**Qué es:** una aplicación **web de uso local** para la gestión de un taller de
automóviles. Sustituye al cuaderno/hoja de cálculo con el que muchos talleres
pequeños llevan las entradas de coches. Su salida principal es el **resguardo de
depósito** (el justificante que se le da al cliente cuando deja el coche), que se
puede imprimir y descargar en PDF.

**Problema que resuelve:** al recibir un coche hay que apuntar cliente, vehículo,
kilómetros, nivel de combustible, trabajos solicitados y fechas, y entregar un
resguardo. Hacerlo a mano es lento, se repiten datos de clientes habituales y los
papeles se pierden. La app centraliza todo, autorrellena los datos de clientes ya
conocidos por la matrícula y guarda un historial consultable.

**Pila tecnológica (stack):**
- Lenguaje: **Python 3.10+**.
- Framework web: **Flask** (microframework WSGI).
- Base de datos: **SQLite** (fichero local, sin servidor aparte), accedida con el
  módulo estándar `sqlite3`.
- Frontend: **HTML5 + CSS3 + JavaScript** (sin framework JS), con **Bootstrap 5.3**
  y **Bootstrap Icons** para la maquetación y **Chart.js 4.4** para las gráficas.
- Plantillas de servidor: **Jinja2** (incluido con Flask).
- PDF: **ReportLab 4** (genera el resguardo en memoria).
- Servidor de producción: **Waitress** (servidor WSGI multiplataforma).
- Empaquetado: **PyInstaller** (genera un `.exe` para que el tribunal lo ejecute
  sin instalar Python).

**Arquitectura (por capas):**
- `modelos/` — capa de acceso a datos. Un módulo por tabla (`cliente`, `vehiculo`,
  `incidencia`, `reparacion`, `foto`) con funciones tipo DAO; `conexion.py`
  centraliza la conexión SQLite (con `row_factory = Row` y `PRAGMA foreign_keys`);
  `esquema.sql` define las tablas.
- `rutas/` — capa de controladores. Cada parte de la app es un **Blueprint** de
  Flask (`principal`, `incidencias`, `agenda`, `clientes`, `vehiculos`, `datos`).
- `servicios/` — lógica de negocio reutilizable: `validaciones.py`,
  `pdf.py` (ReportLab), `csv_datos.py`, `fotos.py`, `formato.py`.
- `templates/` — vistas Jinja2 (una `base.html` y el resto heredan de ella).
- `static/` — `css/estilos.css` y `js/` (cinco scripts: `validaciones.js`,
  `autorrelleno.js`, `graficos.js`, `trabajos.js`, `fotos.js`).
- `config.py` — configuración centralizada (datos del taller y rutas).
- Puntos de entrada: `app.py` (desarrollo, con `debug`), `servidor.py`
  (producción con Waitress en la red local), `lanzar.py` (el que usa el `.exe`:
  arranca el servidor en local y abre el navegador).

**Modelo de datos (relacional):**
`clientes (1)→(N) vehiculos (1)→(N) incidencias (1)→(N) reparaciones / fotos`.
- `clientes`: nombre, cif (DNI/NIE/CIF), telefono, domicilio, numero, cp, poblacion.
- `vehiculos`: matricula (**UNIQUE**, identifica el coche), marca_modelo, cliente_id (FK).
- `incidencias` (cada entrada del coche al taller / orden de trabajo):
  vehiculo_id (FK), fecha_entrada, fecha_entrega, kilometros, combustible,
  estado (**CHECK**: recepcionado, en reparación, terminado, entregado),
  recoger_piezas.
- `reparaciones`: incidencia_id (FK, **ON DELETE CASCADE**), descripcion.
- `fotos`: incidencia_id (FK, **ON DELETE CASCADE**), nombre_archivo (la imagen se
  guarda en disco; en la BD solo va el nombre).

**Funcionalidades principales:**
1. Alta de **ficha/orden de trabajo** con generación del resguardo de depósito.
2. **Autorrelleno por matrícula** (AJAX con `fetch`): si la matrícula ya existe,
   trae del servidor los datos del cliente y del vehículo y los rellena solos.
3. **Resguardo** visible en pantalla (listo para imprimir) y descargable en
   **PDF** (ReportLab, generado en memoria, sin guardar ficheros en el servidor).
4. **Historial** de fichas con **búsqueda** por matrícula, nombre o fecha.
5. **Flujo de estados** (recepcionado → en reparación → terminado → entregado),
   que avanza con un botón; el estado destino lo decide el servidor.
6. **Agenda de entregas**: agrupa las fichas pendientes en vencidas, de hoy y
   próximas según la fecha de entrega.
7. **Gráficas** en el inicio (Chart.js): fichas por estado (tarta) y por mes (barras).
8. **CRUD** de clientes y de vehículos, con reglas (no borrar un cliente con
   coches, ni un coche con fichas).
9. **Importar/Exportar CSV** (clientes, vehículos e historial), compatible con el
   Excel español (separador `;` y codificación UTF-8 con BOM).
10. **Fotos de los daños**: subida múltiple, previsualización, validación de tipo
    y tamaño en el servidor, nombres aleatorios (UUID).

**Decisiones de calidad y seguridad (resáltalas, dan nota):**
- **Consultas parametrizadas** (`?`) en todo el SQL → evita inyección SQL.
- **Validación en el servidor como autoritativa**; el JavaScript solo es comodidad
  para el usuario (avisa mientras escribe), porque el navegador se puede saltar.
- Validaciones propias: **letra de control del DNI/NIE** (algoritmo del módulo 23),
  **matrícula española** (formato actual y antiguo), teléfono y código postal.
- **Transacciones**: el guardado de una ficha (cliente + vehículo + incidencia +
  reparaciones + fotos) va en una sola transacción con `commit`/`rollback`.
- Patrón **POST-Redirect-GET**: tras guardar se redirige, para que recargar la
  página no duplique la ficha.
- Prevención de **path traversal** al servir fotos (`send_from_directory` y
  nombres UUID, nunca el nombre que sube el usuario).
- App **genérica**: para adaptarla a otro taller solo se edita `config.py`.

**Uso de IA (esto debe quedar declarado en la memoria, ver sección 7):** usé un
asistente de IA como apoyo en tres puntos concretos: (a) la hoja de **estilos CSS**
(`static/css/estilos.css`), (b) la **plantilla genérica del PDF** del resguardo
(la maquetación de `servicios/pdf.py` con ReportLab) y (c) el **empaquetado en
`.exe`** con PyInstaller (`gestor_taller.spec` y `construir_exe.ps1`). El resto del
análisis, el diseño de la base de datos y la lógica la trabajé yo.

### 2) Estructura obligatoria de la memoria

La memoria debe incluir, como mínimo, estos apartados (los exige la rúbrica de mi
centro). Mantén esta numeración:

1. **Portada** — título, ciclo (DAM), centro, autor, tutor, curso. Usa
   marcadores `[ENTRE CORCHETES]` para lo que yo deba rellenar; no inventes datos
   personales.
2. **Resumen y *abstract*** — medio folio en español y su traducción al inglés.
3. **Índice** — de contenidos, de figuras y de tablas.
4. **Introducción** — contexto del sector, problema detectado, motivación y breve
   descripción de la solución.
5. **Objetivos** — un objetivo general y varios específicos (en infinitivo,
   concretos y medibles).
6. **Análisis de requisitos**:
   - **Requisitos funcionales** (numerados RF-01, RF-02…), con actor y descripción.
   - **Requisitos no funcionales** (RNF-01…): usabilidad, rendimiento,
     portabilidad, seguridad, mantenibilidad.
   - **Casos de uso** (lista + descripción de los principales) y un **diagrama de
     casos de uso** (ver sección 5 sobre diagramas).
7. **Diseño**:
   - **Arquitectura** del sistema (capas modelos/rutas/servicios/vistas) con
     justificación.
   - **Diseño de la base de datos**: **modelo entidad-relación (E-R)** y modelo
     relacional, con las claves, las restricciones (UNIQUE, CHECK, FK, CASCADE) y
     el porqué de cada tabla.
   - **Diagramas UML**: como mínimo un **diagrama de clases/módulos** y un
     **diagrama de secuencia** de un flujo representativo (recomiendo el del
     autorrelleno por matrícula o el de generar el resguardo en PDF).
   - **Diseño de la interfaz** (pantallas principales y por qué).
8. **Implementación** — recorrido por las capas y las decisiones técnicas
   importantes (las de la lista de "calidad y seguridad"). Incluye fragmentos de
   código **cortos y comentados** solo cuando aporten (no pegues ficheros enteros).
9. **Pruebas** — qué se probó y cómo (pruebas manuales por funcionalidad, casos
   límite de validación, prueba del CSV de ida y vuelta, prueba del `.exe` en un
   equipo sin Python). Presenta una **tabla de pruebas** (caso, entrada, resultado
   esperado, resultado obtenido).
10. **Despliegue** — modos de ejecución (desarrollo, producción con Waitress en la
    red local, y `.exe` para el tribunal) y, brevemente, la opción de nube.
11. **Manual de usuario** — con pasos y referencias a las capturas de pantalla
    (marca dónde irá cada captura con `[CAPTURA: …]`).
12. **Manual técnico** — requisitos, instalación, configuración (`config.py`),
    estructura de carpetas y cómo generar el `.exe`.
13. **Conclusiones** — qué he aprendido, objetivos cumplidos, dificultades.
14. **Líneas futuras** — mejoras realistas (ver ideas en la sección 6).
15. **Bibliografía** — según la sección 6.
16. **Anexos** (opcional) — diagramas grandes, listados, etc.

### 3) Estilo y voz (esto es lo que hace que suene a mí)

- Escribe en **español de España**, registro técnico pero natural, como un
  estudiante de 2.º de DAM competente; **no** como una consultora ni como un
  folleto comercial. Nada de "potenciar sinergias", "solución robusta de última
  generación", etc.
- **Primera persona** cuando cuente decisiones ("decidí usar SQLite porque…",
  "para evitar duplicar la ficha apliqué…"). El resto, impersonal.
- Frases de longitud variada. Evita el patrón "Además… Asimismo… Por otro lado…"
  repetido. Evita listas con viñetas en cada párrafo: alterna prosa y listas.
- **No seas redundante**: no repitas la misma idea en la introducción, los
  objetivos y las conclusiones con otras palabras. Cada apartado aporta algo nuevo.
- Coherencia con el código: el código real está comentado en español con un tono
  cercano ("uso parámetros para evitar inyección", "compruebo que la foto es de
  esta ficha"). La memoria debe sonar de la misma persona.
- Términos técnicos en su forma habitual (no traduzcas "framework", "commit",
  "endpoint", "blueprint"); pero explícalos la primera vez.
- Cuando expliques una decisión, da el **porqué** y, si la hay, la **alternativa
  descartada** (p. ej. "SQLite frente a MySQL"). Eso demuestra criterio.
- Longitud orientativa: [PON TU OBJETIVO, p. ej. 35–50 páginas sin anexos].
  Ajusta densidad sin rellenar por rellenar.

### 4) Reglas para no meter la pata

- **No inventes** datos, cifras, resultados de pruebas, ni funcionalidades que no
  estén en el contexto de arriba. Si te falta un dato mío, deja `[RELLENAR: …]`.
- No describas tecnologías que no uso (no hay ORM tipo SQLAlchemy, no hay API REST
  externa, no hay login de usuarios: dilo si hace falta, pero no lo inventes).
- Si una afirmación necesita respaldo (p. ej. "Flask es un microframework WSGI"),
  márcala para citar la fuente correspondiente de la sección 6.

### 5) Diagramas (los exige la rúbrica: UML y E-R)

No puedes generar imágenes, pero **sí** el código para crearlas. Para cada
diagrama dame el bloque listo para pegar en **Mermaid** (https://mermaid.live) o
en **PlantUML**, y una nota de cómo exportarlo a PNG para incrustarlo en
LibreOffice Writer. Genera al menos:

- **E-R / relacional** con las cinco tablas, claves y cardinalidades. Punto de
  partida (verifícalo con el contexto y mejóralo):

  ```mermaid
  erDiagram
      CLIENTES ||--o{ VEHICULOS : tiene
      VEHICULOS ||--o{ INCIDENCIAS : registra
      INCIDENCIAS ||--o{ REPARACIONES : incluye
      INCIDENCIAS ||--o{ FOTOS : adjunta
      CLIENTES {
        int id PK
        string nombre
        string cif
        string telefono
        string domicilio
        string numero
        string cp
        string poblacion
      }
      VEHICULOS {
        int id PK
        string matricula UK
        string marca_modelo
        int cliente_id FK
      }
      INCIDENCIAS {
        int id PK
        int vehiculo_id FK
        string fecha_entrada
        string fecha_entrega
        int kilometros
        string combustible
        string estado
        string recoger_piezas
      }
      REPARACIONES {
        int id PK
        int incidencia_id FK
        string descripcion
      }
      FOTOS {
        int id PK
        int incidencia_id FK
        string nombre_archivo
      }
  ```

- **Diagrama de casos de uso** (actor: *empleado del taller*) con los casos:
  registrar ficha, autorrellenar por matrícula, generar/descargar resguardo,
  consultar historial, avanzar estado, ver agenda, gestionar clientes, gestionar
  vehículos, importar/exportar CSV, gestionar fotos.
- **Diagrama de secuencia** del **autorrelleno por matrícula**: navegador →
  `GET /incidencias/matricula/<matricula>` → ruta → `vehiculo.datos_para_autorrelleno`
  → SQLite → respuesta JSON → relleno de campos en el formulario.
- (Opcional) **Diagrama de secuencia** de "descargar resguardo PDF":
  `GET /incidencias/<id>/pdf` → carga de datos → `generar_resguardo_pdf` (ReportLab)
  → `send_file` con el PDF en memoria.

### 6) Bibliografía y citas (criterio independiente de la rúbrica)

La rúbrica pide **citar en el texto** y recoger todo en bibliografía. Reglas:

- Usa **estilo APA 7.ª** (o el que indique mi centro: [CONFIRMAR]).
- **Cita en el texto** cada vez que una afirmación venga de una fuente
  (p. ej. "(Pallets Projects, s.f.)"), y que esa fuente aparezca luego en la lista.
- **No inventes** referencias, autores, ISBN ni URLs. Usa solo fuentes que yo
  pueda comprobar. Para cada fuente añade **fecha de consulta**.
- Prioriza **documentación oficial** y fuentes primarias. Lista base recomendada
  (verifica cada URL antes de citarla):
  - Pallets Projects. *Flask Documentation*. https://flask.palletsprojects.com/
  - Pallets Projects. *Jinja Documentation*. https://jinja.palletsprojects.com/
  - Pallets Projects. *Werkzeug Documentation*. https://werkzeug.palletsprojects.com/
  - Python Software Foundation. *sqlite3 — DB-API 2.0 interface for SQLite*.
    https://docs.python.org/3/library/sqlite3.html
  - SQLite. *Documentation*. https://www.sqlite.org/docs.html
  - ReportLab. *ReportLab User Guide*. https://www.reportlab.com/docs/reportlab-userguide.pdf
  - Bootstrap. *Documentation v5.3*. https://getbootstrap.com/docs/5.3/
  - Chart.js. *Documentation*. https://www.chartjs.org/docs/latest/
  - Pylons Project. *Waitress Documentation*. https://docs.pylonsproject.org/projects/waitress/
  - PyInstaller. *Documentation*. https://pyinstaller.org/en/stable/
  - MDN Web Docs (HTML/CSS/JS). https://developer.mozilla.org/
  - Python Software Foundation. *PEP 8 – Style Guide for Python Code*.
    https://peps.python.org/pep-0008/
  - OWASP. *SQL Injection Prevention Cheat Sheet* y *Top Ten*. https://owasp.org/
  - Grinberg, M. (2018). *Flask Web Development* (2.ª ed.). O'Reilly. (libro real;
    cítalo solo si lo consulto de verdad).
  - Para metodología/UML/requisitos, un manual de ingeniería del software de
    referencia (p. ej. Sommerville o Pressman) **solo si lo uso**.
  - Para la **letra del DNI/NIE** y el **formato de matrícula española**: cita la
    fuente oficial (BOE / DGT). **No** inventes el número de boletín; pídeme que lo
    verifique y deja `[VERIFICAR REFERENCIA BOE/DGT]`.

### 7) Declaración de uso de IA (apartado obligatorio en mi memoria)

Incluye un apartado breve y honesto (media página) titulado **"Uso de herramientas
de inteligencia artificial"**, redactado en primera persona, que diga con
naturalidad que utilicé un asistente de IA como **herramienta de apoyo** en:
1. el diseño de la **hoja de estilos CSS**,
2. la **plantilla genérica del documento PDF** del resguardo (maquetación con
   ReportLab), y
3. el **empaquetado del programa en un ejecutable `.exe`** con PyInstaller.

Deja claro que revisé, entendí y adapté ese material, y que el análisis, el diseño
de datos y la lógica de la aplicación son trabajo propio. Enfócalo como uso
responsable de una herramienta (igual que se usa documentación o Stack Overflow),
no como una disculpa.

### 8) Formato de salida

- Devuélveme **un capítulo cada vez**, en Markdown, con los encabezados jerárquicos
  bien puestos (para poder pegarlo y maquetarlo en LibreOffice Writer).
- Marca con `[CAPTURA: descripción]` dónde debo insertar capturas y con
  `[FIGURA N: …]` las figuras/diagramas, numeradas.
- Al final de cada capítulo, lístame en 3–5 puntos **qué debo revisar o rellenar
  yo** antes de darlo por bueno.
- **Empieza preguntándome** los datos que te falten para la portada y el alcance
  (nombre, centro, tutor, curso, longitud objetivo, estilo de cita) y **espera mi
  respuesta** antes de generar el capítulo 1.
