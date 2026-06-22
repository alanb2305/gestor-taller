# Guion 2 · Prompt para crear la PRESENTACIÓN (LibreOffice Impress)

> **Cómo usar este fichero.** Es un *prompt* para que un asistente (Claude) te
> genere el **contenido y el guion de cada diapositiva**. La presentación es el
> apoyo de tu demo en vivo, no el protagonista: la rúbrica penaliza "leer las
> diapositivas" y premia diapositivas claras con poco texto. Por eso este guion
> pide **poco texto en pantalla** y **notas del orador** (lo que dirás tú).
>
> Trabajas con **LibreOffice Impress**. Al final hay instrucciones para montarla
> rápido (incluido el truco del **esquema** para crear las diapositivas en
> segundos) y para exportar a `.pptx`/PDF por si el equipo del tribunal usa otro
> programa.

---

## Antes de pedir nada: decide el tiempo

La rúbrica valora la **gestión del tiempo**. Mira cuántos minutos tienes
([RELLENAR, p. ej. 10–15 min]) y cuéntalos así: ~1 minuto por diapositiva de
hablar + **4–5 minutos para la demo en vivo**. Con 10–12 diapositivas vas bien.
Dilo en el prompt para que ajuste la cantidad.

---

## EL PROMPT (a partir de aquí, pégaselo al asistente)

Ayúdame a preparar la **presentación de la defensa** de mi TFG del ciclo de
**Desarrollo de Aplicaciones Multiplataforma (DAM)**. Soy estudiante de **segundo
año**. La presentación es el **apoyo visual de una demo en vivo**; no quiero
diapositivas con párrafos: quiero **poco texto en pantalla** y, aparte, las
**notas del orador** con lo que diré yo.

### Restricciones

- Tiempo total de exposición: **[RELLENAR] minutos**, de los cuales reservo
  **4–5 minutos a la demo en vivo** del programa.
- Número de diapositivas: ajústalo al tiempo (orientativo: **10–12**).
- Regla de texto: **máximo ~6 líneas** y **~6 palabras por línea** por diapositiva;
  títulos cortos; nada de frases que yo pueda leer literalmente.
- Idioma: español. Tono: técnico pero cercano, de estudiante que **domina** su
  proyecto (no comercial).

### Contexto del proyecto (úsalo como única verdad; no inventes)

**GestorTaller**: aplicación **web de uso local** para gestionar un taller de
automóviles (clientes, vehículos y órdenes de trabajo) cuya salida principal es el
**resguardo de depósito** en PDF (imprimible y descargable).

- **Stack:** Python + **Flask**, base de datos **SQLite** (`sqlite3`), frontend
  **HTML/CSS/JS** con **Bootstrap 5** y **Chart.js**, plantillas **Jinja2**, PDF con
  **ReportLab**, servidor **Waitress**, empaquetado a `.exe` con **PyInstaller**.
- **Arquitectura por capas:** `modelos/` (acceso a datos, un módulo por tabla),
  `rutas/` (controladores como **Blueprints** de Flask), `servicios/` (lógica:
  validaciones, PDF, CSV, fotos), `templates/` (vistas Jinja2), `static/` (CSS/JS).
- **Datos:** `clientes → vehiculos → incidencias → reparaciones/fotos`
  (claves foráneas, `matricula` única, estados con `CHECK`, borrado en cascada).
- **Funcionalidades clave:** alta de ficha + resguardo; **autorrelleno por
  matrícula** (AJAX); resguardo en **PDF** (ReportLab, en memoria) e impresión;
  **historial** con búsqueda; **flujo de estados** (recepcionado → en reparación →
  terminado → entregado); **agenda de entregas** (vencidas/hoy/próximas);
  **gráficas** (tarta por estado, barras por mes); **CRUD** de clientes y vehículos;
  **import/export CSV** (compatible con Excel español); **fotos de los daños**
  (subida, previsualización y validación en servidor).
- **Puntos fuertes técnicos (para presumir con criterio):** consultas SQL
  **parametrizadas** (anti-inyección); **validación en servidor** como la que
  cuenta (incluida **letra del DNI/NIE** y **matrícula española**); **transacciones**
  con commit/rollback; patrón **POST-Redirect-GET**; prevención de **path traversal**
  al servir imágenes; app **genérica** configurable desde `config.py`.
- **Despliegue:** ejecutable en desarrollo (`app.py`), en red local con Waitress
  (`servidor.py`) y como **`.exe`** que abre solo el navegador (`lanzar.py`), para
  que el tribunal lo pruebe sin instalar nada.
- **Uso de IA (decláralo en la diapositiva de cierre, sin dramatizar):** apoyo de
  un asistente de IA en la **hoja de estilos CSS**, la **plantilla del PDF** del
  resguardo y el **empaquetado `.exe`**; el resto es trabajo propio.

### Estructura de diapositivas que quiero (ajústala al tiempo)

Para **cada** diapositiva dame: (a) **título**, (b) **bullets en pantalla**
(poquísimos), (c) **notas del orador** (2–5 frases, lo que diré), (d) **idea
visual** (qué imagen/captura/diagrama poner) y (e) **tiempo estimado**.

1. **Portada** — nombre del proyecto, subtítulo de una línea, mi nombre, ciclo,
   centro, tutor, fecha. (Marca lo personal con `[RELLENAR]`.)
2. **El problema** — cómo se gestiona hoy un taller pequeño (papel/Excel) y qué
   falla. Engancha; aquí va el "valor del software".
3. **La solución en una frase** — qué es GestorTaller y para quién.
4. **Objetivos** — 3–4, claros.
5. **Tecnologías** — el stack, con logos; una frase de por qué cada bloque.
6. **Arquitectura** — diagrama de capas (modelos/rutas/servicios/vistas) + base de
   datos; explica el reparto de responsabilidades.
7. **Modelo de datos** — el diagrama E-R resumido y la idea de las relaciones.
8. **DEMO EN VIVO** — diapositiva-marcador (solo el título "Demostración" y el
   guion mínimo en notas). Aquí cambio a la aplicación. (El paso a paso está en mi
   Guion 3.)
9. **Decisiones técnicas** — 3 que den nota: validación en servidor (DNI/matrícula),
   seguridad (SQL parametrizado + transacciones), y el `.exe` para el tribunal.
10. **Retos y cómo los resolví** — 1–2 problemas reales y la solución (p. ej. que
    el `.exe` encuentre las plantillas y guarde la base de datos junto al programa).
11. **Conclusiones y líneas futuras** — qué he aprendido + mejoras realistas
    (login, protección CSRF, control de versiones de piezas/precios, etc.).
12. **Cierre** — agradecimiento, nota breve de uso de IA y "¿preguntas?".

### Estilo visual

- Paleta coherente con la app: color de acento **naranja `#e07b00`** sobre
  fondo claro, grises para texto secundario (`#555`). Una o dos tipografías
  legibles (p. ej. una sans para títulos y otra para cuerpo).
- Una idea por diapositiva. Capturas reales del programa mejor que texto.
- Plantilla sobria y consistente (misma posición de título, número de página,
  pie discreto con el nombre del proyecto).
- Sugiéreme para cada captura **qué pantalla** capturar (inicio con gráficas,
  formulario con autorrelleno, resguardo, PDF, historial, agenda).

### Formato de salida

1. Primero, un **esquema en texto plano** con solo **título de cada diapositiva**
   y, debajo, los bullets con tabulación, para **importarlo de golpe** en Impress
   (Ver → Esquema). Sepárame claramente esta parte.
2. Después, el **detalle por diapositiva** (bullets + notas del orador + idea
   visual + tiempo).
3. Acaba con una **lista de capturas** que debo hacer y una **checklist de
   ensayo** (tiempo, conexiones, plan B si falla la demo).
4. **Empieza preguntándome** el tiempo de exposición y los datos de la portada, y
   **espera mi respuesta** antes de generar nada.

---

## Cómo montarla en LibreOffice Impress (rápido)

1. **Crear las diapositivas desde el esquema.** Abre Impress → menú
   **Ver ▸ Esquema**. Pega ahí el esquema en texto: cada línea sin sangría es el
   **título** de una diapositiva nueva; cada línea con **tabulación** es un bullet.
   En segundos tienes todas las diapositivas creadas. Vuelve a **Ver ▸ Normal**.
2. **Notas del orador.** Menú **Ver ▸ Notas** y pega, en cada diapositiva, lo que
   dirás. En el ensayo usa la **Vista del presentador** (verás tus notas y el
   cronómetro mientras el público ve solo la diapositiva).
3. **Plantilla/diseño.** **Diapositiva ▸ Propiedades** y **Ver ▸ Patrón de
   diapositivas** para fijar colores, tipografía y el pie. Aplica el patrón a todas.
4. **Capturas.** En Windows usa **Recortes** (Win+Shift+S). Inserta con
   **Insertar ▸ Imagen**. Recórtalas para que se vea solo lo importante.
5. **Diagramas.** Genera el E-R / arquitectura con Mermaid (https://mermaid.live)
   o PlantUML, expórtalos a PNG y enállos como imagen.
6. **Compatibilidad con el equipo del tribunal.** Guarda el original en `.odp`,
   pero **exporta también a `.pptx`** (Archivo ▸ Guardar como) **y a PDF**
   (Archivo ▸ Exportar a PDF). Lleva las tres versiones en un USB: si el portátil
   del aula no tiene LibreOffice, el PDF siempre abre.
7. **Fuentes.** Si usas una tipografía poco común, al pasar a otro equipo puede
   cambiar; quédate con fuentes estándar o **incrusta las fuentes** al exportar a
   PDF para que no se descoloque.
