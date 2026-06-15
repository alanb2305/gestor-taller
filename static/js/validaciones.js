/* ===========================================================================
   Validación del formulario en el navegador.

   IMPORTANTE: esto es SOLO para avisar al usuario cuanto antes y que la
   experiencia sea cómoda. La validación que de verdad cuenta está en el
   servidor (servicios/validaciones.py), porque el navegador se puede saltar
   (desactivando JavaScript, por ejemplo) y nunca hay que fiarse del cliente.

   Por eso aquí repetimos solo las comprobaciones más útiles para el usuario;
   el DNI/CIF, por ejemplo, lo valida a fondo el servidor.
   =========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  const formulario = document.getElementById("form-incidencia");
  if (!formulario) return;   // si no estamos en la página del formulario, nada

  const entrada = document.getElementById("fecha_entrada");
  const entrega = document.getElementById("fecha_entrega");

  // -------------------------------------------------------------------------
  // Mayúsculas automáticas mientras se escribe en DNI/CIF y matrícula.
  // (La clase text-uppercase de Bootstrap solo lo muestra en mayúsculas, pero
  //  el valor real que se envía hay que cambiarlo a mano, que es esto.)
  // -------------------------------------------------------------------------
  ["cif", "matricula"].forEach(function (id) {
    const campo = document.getElementById(id);
    if (campo) {
      campo.addEventListener("input", function () {
        campo.value = campo.value.toUpperCase();
      });
    }
  });

  // -------------------------------------------------------------------------
  // La entrega no puede ser anterior a la entrada: le ponemos al calendario
  // de "entrega" un mínimo igual a la fecha de entrada.
  // -------------------------------------------------------------------------
  function ajustarMinimoEntrega() {
    if (entrada && entrega && entrada.value) {
      entrega.min = entrada.value;
    }
  }
  ajustarMinimoEntrega();
  if (entrada) entrada.addEventListener("change", ajustarMinimoEntrega);

  // -------------------------------------------------------------------------
  // Expresiones regulares: las mismas reglas que usa el servidor.
  // -------------------------------------------------------------------------
  const reTelefono = /^[6789]\d{8}$/;                       // 9 dígitos, empieza 6/7/8/9
  const reCp       = /^\d{5}$/;                             // 5 dígitos
  const reKm       = /^\d+$/;                               // solo números

  function matriculaValida(texto) {
    const t = texto.toUpperCase().replace(/[-\s]/g, "");
    const nueva   = /^\d{4}[BCDFGHJKLMNPRSTVWXYZ]{3}$/;      // 1234BCD
    const antigua = /^[A-Z]{1,2}\d{4}[A-Z]{1,2}$/;          // TE1234A
    return nueva.test(t) || antigua.test(t);
  }

  // -------------------------------------------------------------------------
  // Ayudas para pintar/quitar el error de un campo (borde rojo + mensaje).
  // El mensaje va en el <div class="invalid-feedback"> que hay justo debajo
  // del input en el HTML.
  // -------------------------------------------------------------------------
  function marcarError(campo, mensaje) {
    campo.classList.add("is-invalid");
    const aviso = campo.nextElementSibling;
    if (aviso && aviso.classList.contains("invalid-feedback")) {
      aviso.textContent = mensaje;
    }
  }

  function limpiarError(campo) {
    campo.classList.remove("is-invalid");
  }

  // -------------------------------------------------------------------------
  // Al enviar el formulario, comprobamos todo. Si algo falla, paramos el
  // envío (preventDefault) y llevamos al usuario al primer campo con error.
  // -------------------------------------------------------------------------
  formulario.addEventListener("submit", function (evento) {
    let valido = true;
    let primerError = null;

    // Función corta para no repetir: si la condición falla, marca el error.
    function comprobar(campo, condicion, mensaje) {
      if (!campo) return;
      if (condicion) {
        limpiarError(campo);
      } else {
        marcarError(campo, mensaje);
        valido = false;
        if (!primerError) primerError = campo;
      }
    }

    const v = (id) => {
      const campo = document.getElementById(id);
      return campo ? campo.value.trim() : "";
    };

    // 1) Campos obligatorios (los mismos que en el servidor).
    comprobar(document.getElementById("fecha_entrada"), v("fecha_entrada") !== "",
              "La fecha de entrada es obligatoria.");
    comprobar(document.getElementById("fecha_entrega"), v("fecha_entrega") !== "",
              "La fecha de entrega es obligatoria.");
    comprobar(document.getElementById("nombre"), v("nombre") !== "",
              "El nombre del cliente es obligatorio.");
    comprobar(document.getElementById("marca_modelo"), v("marca_modelo") !== "",
              "La marca y el modelo son obligatorios.");
    comprobar(document.getElementById("matricula"), v("matricula") !== "",
              "La matrícula es obligatoria.");

    // 2) Formato (solo si el campo tiene algo escrito; si está vacío, lo deja
    //    pasar y, si era obligatorio, ya lo habrá cazado el paso anterior).
    if (v("telefono") !== "")
      comprobar(document.getElementById("telefono"),
                reTelefono.test(v("telefono").replace(/\s/g, "")),
                "El teléfono debe tener 9 dígitos y empezar por 6, 7, 8 o 9.");

    if (v("cp") !== "")
      comprobar(document.getElementById("cp"), reCp.test(v("cp")),
                "El código postal debe tener 5 dígitos.");

    if (v("kilometros") !== "")
      comprobar(document.getElementById("kilometros"), reKm.test(v("kilometros")),
                "Los kilómetros deben ser solo números.");

    if (v("matricula") !== "")
      comprobar(document.getElementById("matricula"), matriculaValida(v("matricula")),
                "La matrícula no tiene un formato español válido.");

    // 3) Coherencia de fechas: la entrega no puede ser anterior a la entrada.
    //    Las fechas vienen en formato ISO (AAAA-MM-DD), que se puede comparar
    //    como texto directamente porque ordena igual que por fecha.
    if (v("fecha_entrada") !== "" && v("fecha_entrega") !== ""
        && v("fecha_entrega") < v("fecha_entrada")) {
      marcarError(document.getElementById("fecha_entrega"),
                  "La entrega no puede ser anterior a la entrada.");
      valido = false;
      if (!primerError) primerError = document.getElementById("fecha_entrega");
    }

    // Si hay algún error, no enviamos y vamos al primero.
    if (!valido) {
      evento.preventDefault();
      if (primerError) {
        primerError.scrollIntoView({ behavior: "smooth", block: "center" });
        primerError.focus();
      }
    }
  });

});
