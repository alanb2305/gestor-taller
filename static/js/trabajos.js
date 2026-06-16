/* ===========================================================================
   Trabajos a realizar: añadir y quitar líneas.

   En vez de mostrar un número fijo de líneas, empezamos con una y el usuario
   añade las que necesite con el botón "+". Cada línea tiene una papelera para
   quitarla. Todas las cajas se llaman "reparacion": el servidor las recoge
   juntas con getlist() y descarta las vacías, así que da igual cuántas haya.

   Si no hubiera JavaScript, el formulario sigue funcionando: se ve la línea (o
   las líneas) que pinta la plantilla y se pueden enviar igual.
   =========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  const lista = document.getElementById("lista-trabajos");
  const anadir = document.getElementById("anadir-trabajo");
  if (!lista || !anadir) return;   // no estamos en el formulario

  // Botón "+": añade una línea vacía y deja el cursor dentro para escribir.
  anadir.addEventListener("click", function () {
    const fila = crearFila();
    lista.appendChild(fila);
    fila.querySelector("input").focus();
    renumerar();
  });

  // Papelera: quita la línea. Usamos delegación (un solo listener en la lista)
  // para que funcione también con las filas que se añaden después.
  lista.addEventListener("click", function (evento) {
    const botonQuitar = evento.target.closest(".quitar-trabajo");
    if (!botonQuitar) return;

    const filas = lista.querySelectorAll(".fila-trabajo");
    // Dejamos siempre al menos una línea: si es la última, en vez de quitarla
    // solo la vaciamos, para que el formulario no se quede sin ninguna.
    if (filas.length <= 1) {
      lista.querySelector(".fila-trabajo input").value = "";
    } else {
      botonQuitar.closest(".fila-trabajo").remove();
    }
    renumerar();
  });

  // Crea una fila nueva (caja de texto + papelera) y la devuelve. El HTML es
  // fijo (no metemos datos escritos por el usuario), así que es seguro.
  function crearFila() {
    const fila = document.createElement("div");
    fila.className = "input-group mb-2 fila-trabajo";
    fila.innerHTML =
      '<input type="text" name="reparacion" class="form-control" placeholder="Trabajo">' +
      '<button type="button" class="btn btn-outline-secondary quitar-trabajo" ' +
      'title="Quitar este trabajo"><i class="bi bi-trash"></i></button>';
    return fila;
  }

  // Renumera los textos de ayuda: Trabajo 1, Trabajo 2, Trabajo 3...
  function renumerar() {
    lista.querySelectorAll(".fila-trabajo input").forEach(function (input, i) {
      input.placeholder = "Trabajo " + (i + 1);
    });
  }

});
