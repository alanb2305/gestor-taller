/* ===========================================================================
   Gráficas de la pantalla de inicio (Chart.js).

   Pedimos los datos al servidor (/estadisticas) y dibujamos dos gráficas:
     - Fichas por estado  -> tarta (doughnut)
     - Fichas por mes     -> barras

   Igual que en el resto del proyecto, los datos los calcula el servidor; aquí
   solo los pintamos. Chart.js se carga desde un CDN en inicio.html.
   =========================================================================== */

document.addEventListener("DOMContentLoaded", async function () {

  // Si no estamos en la pantalla de inicio (no existe el contenedor), nada.
  const contenedor = document.getElementById("graficas");
  if (!contenedor) return;

  // Pedimos los datos al servidor. Si falla, no rompemos la página.
  let datos;
  try {
    const respuesta = await fetch("/estadisticas");
    datos = await respuesta.json();
  } catch (error) {
    console.error("No se pudieron cargar las estadísticas:", error);
    return;
  }

  // ¿Hay datos? Sumamos las fichas de todos los estados; si es 0, no hay nada
  // que pintar: escondemos las gráficas y mostramos un aviso.
  const totalFichas = datos.por_estado.datos.reduce((a, b) => a + b, 0);
  if (totalFichas === 0) {
    contenedor.style.display = "none";
    document.getElementById("sin-datos").style.display = "block";
    return;
  }

  // Color de acento de la app y colores de cada estado (los mismos que las
  // etiquetas del historial, para que se reconozcan de un vistazo).
  const ACENTO = "#e07b00";
  const COLOR_ESTADO = {
    "recepcionado":  "#6c757d",   // gris
    "en reparación": "#ffc107",   // amarillo
    "terminado":     "#0dcaf0",   // azul
    "entregado":     "#198754",   // verde
  };

  // 1) Fichas por estado: gráfica de tarta.
  new Chart(document.getElementById("grafica-estado"), {
    type: "doughnut",
    data: {
      labels: datos.por_estado.labels,
      datasets: [{
        data: datos.por_estado.datos,
        backgroundColor: datos.por_estado.labels.map(e => COLOR_ESTADO[e] || ACENTO),
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
    },
  });

  // 2) Fichas por mes: barras verticales.
  new Chart(document.getElementById("grafica-mes"), {
    type: "bar",
    data: {
      labels: datos.por_mes.labels,
      datasets: [{ label: "Fichas", data: datos.por_mes.datos,
                   backgroundColor: ACENTO }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      // precision: 0 evita decimales en el eje (las fichas se cuentan enteras).
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  });

});
