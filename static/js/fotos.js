/* ===========================================================================
   Previsualización de las fotos de los daños en el formulario.

   Al elegir las fotos en el alta de la ficha, muestro una miniatura de cada
   una debajo del campo, así se ve qué se va a subir antes de generar el
   resguardo. Las imágenes viajan con el formulario; aquí solo se previsualizan.
   =========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  const campo = document.getElementById("fotos");
  const caja = document.getElementById("previsualizacion-fotos");
  if (!campo || !caja) return;   // si no estamos en el formulario, no hacemos nada

  // Cada vez que se eligen archivos, repinto las miniaturas desde cero.
  campo.addEventListener("change", function () {
    caja.innerHTML = "";

    // campo.files es la lista de archivos elegidos. Solo muestro las imágenes
    // (el tipo de verdad lo comprueba el servidor al subirlas).
    for (const archivo of campo.files) {
      if (!archivo.type.startsWith("image/")) continue;

      const img = document.createElement("img");
      // createObjectURL da una URL temporal a la imagen ya elegida, sin tener
      // que leer el archivo entero ni subirlo todavía.
      img.src = URL.createObjectURL(archivo);
      img.alt = archivo.name;
      // Cuando la miniatura ya se ha pintado, libero la URL temporal (si no, se
      // quedaría reservada en memoria).
      img.addEventListener("load", function () {
        URL.revokeObjectURL(img.src);
      });
      caja.appendChild(img);
    }
  });

});
