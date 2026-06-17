/* ===========================================================================
   Trabajos a realizar: añadir y quitar líneas.

   Empiezo con una línea y el usuario añade las que necesite con el botón "+".
   Cada una tiene una papelera para quitarla. Todas se llaman "reparacion": el
   servidor las recoge juntas con getlist() y descarta las vacías. Sin
   JavaScript el formulario sigue funcionando con la línea que pinta la plantilla.
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

  // Papelera: quita la línea. Uso delegación (un listener en la lista) para que
  // funcione también con las filas que se añaden después.
  lista.addEventListener("click", function (evento) {
    const botonQuitar = evento.target.closest(".quitar-trabajo");
    if (!botonQuitar) return;

    const filas = lista.querySelectorAll(".fila-trabajo");
    // Dejo siempre al menos una línea: si es la última, en vez de quitarla solo
    // la vacío, para que el formulario no se quede sin ninguna.
    if (filas.length <= 1) {
      lista.querySelector(".fila-trabajo input").value = "";
    } else {
      botonQuitar.closest(".fila-trabajo").remove();
    }
    renumerar();
  });

  // Crea una fila nueva (caja de texto + papelera) y la devuelve.
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
