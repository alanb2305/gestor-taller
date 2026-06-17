/* ===========================================================================
   Validación del formulario en el navegador.

   Esto es solo para avisar al usuario cuanto antes; la validación que cuenta
   está en el servidor (el navegador se puede saltar). La idea es avisar mientras
   se escribe: los campos con formato (teléfono, CP, km, matrícula y DNI/CIF) se
   comprueban al salir del campo y, si ya están en rojo, en cada tecla, para que
   el aviso desaparezca al corregir. Los obligatorios vacíos se avisan al enviar.
   =========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  const formulario = document.getElementById("form-incidencia");
  if (!formulario) return;   // si no estamos en la página del formulario, nada

  const entrada = document.getElementById("fecha_entrada");
  const entrega = document.getElementById("fecha_entrega");

  // Letras de control del DNI/NIE (las mismas que el servidor).
  const LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE";

  // Expresiones regulares: las mismas reglas que el servidor.
  const reTelefono = /^[6789]\d{8}$/;   // 9 dígitos, empieza por 6/7/8/9
  const reCp       = /^\d{5}$/;         // 5 dígitos
  const reKm       = /^\d+$/;           // solo números

  // Mensajes de los campos obligatorios (los mismos que en el servidor).
  const OBLIGATORIOS = {
    fecha_entrada: "La fecha de entrada es obligatoria.",
    fecha_entrega: "La fecha de entrega es obligatoria.",
    nombre:        "El nombre del cliente es obligatorio.",
    marca_modelo:  "La marca y el modelo son obligatorios.",
    matricula:     "La matrícula es obligatoria.",
  };

  // Reglas de formato por campo. validar() devuelve true/false; si el campo
  // está vacío lo da por bueno (lo obligatorio se mira aparte). Es el mismo
  // criterio que las funciones de servicios/validaciones.py.
  const REGLAS = {
    telefono: {
      validar: (v) => v === "" || reTelefono.test(v.replace(/\s/g, "")),
      mensaje: "El teléfono debe tener 9 dígitos y empezar por 6, 7, 8 o 9.",
    },
    cp: {
      validar: (v) => v === "" || reCp.test(v),
      mensaje: "El código postal debe tener 5 dígitos.",
    },
    kilometros: {
      validar: (v) => v === "" || reKm.test(v),
      mensaje: "Los kilómetros deben ser solo números.",
    },
    matricula: {
      validar: (v) => v === "" || matriculaValida(v),
      mensaje: "La matrícula no tiene un formato español válido.",
    },
    cif: {
      validar: (v) => documentoValido(v),
      mensaje: "El DNI/NIE/CIF no es válido.",
    },
  };

  // Campos con regla de formato: son los que validamos en vivo (blur + input).
  const CAMPOS_FORMATO = ["telefono", "cp", "kilometros", "matricula", "cif"];

  // Mayúsculas automáticas en DNI/CIF y matrícula. (text-uppercase de Bootstrap
  // solo lo MUESTRA en mayúsculas; el valor que se envía hay que cambiarlo aquí.)
  ["cif", "matricula"].forEach(function (id) {
    const campo = document.getElementById(id);
    if (campo) {
      campo.addEventListener("input", function () {
        campo.value = campo.value.toUpperCase();
      });
    }
  });

  // La entrega no puede ser anterior a la entrada: pongo al calendario de
  // "entrega" un mínimo igual a la fecha de entrada.
  function ajustarMinimoEntrega() {
    if (entrada && entrega && entrada.value) {
      entrega.min = entrada.value;
    }
  }
  ajustarMinimoEntrega();

  // Validación del DNI/NIE/CIF (mismo algoritmo que el servidor). El CIF solo
  // se comprueba de formato.
  function documentoValido(texto) {
    if (texto === "") return true;   // campo opcional
    const t = texto.toUpperCase().replace(/[-\s]/g, "");

    if (/^\d{8}[A-Z]$/.test(t)) {                       // DNI
      return t[8] === LETRAS_DNI[parseInt(t.slice(0, 8), 10) % 23];
    }
    if (/^[XYZ]\d{7}[A-Z]$/.test(t)) {                  // NIE (X/Y/Z = 0/1/2)
      const inicio = { X: "0", Y: "1", Z: "2" }[t[0]];
      const numero = parseInt(inicio + t.slice(1, 8), 10);
      return t[8] === LETRAS_DNI[numero % 23];
    }
    if (/^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$/.test(t)) { // CIF (solo formato)
      return true;
    }
    return false;
  }

  // Matrícula española: formato nuevo (1234BCD) o antiguo (TE1234A).
  function matriculaValida(texto) {
    const t = texto.toUpperCase().replace(/[-\s]/g, "");
    const nueva   = /^\d{4}[BCDFGHJKLMNPRSTVWXYZ]{3}$/;
    const antigua = /^[A-Z]{1,2}\d{4}[A-Z]{1,2}$/;
    return nueva.test(t) || antigua.test(t);
  }

  // Localiza el <div class="invalid-feedback"> de un campo (donde va el mensaje).
  // Lo busco entre los hermanos siguientes (saltando otros avisos, como el del
  // autorrelleno) y, si no, dentro del contenedor del campo.
  function feedbackDe(campo) {
    let el = campo.nextElementSibling;
    while (el && !el.classList.contains("invalid-feedback")) {
      el = el.nextElementSibling;
    }
    if (!el && campo.parentElement) {
      el = campo.parentElement.querySelector(".invalid-feedback");
    }
    return el;
  }

  // Pintar / quitar el error de un campo (borde rojo + mensaje).
  function marcarError(campo, mensaje) {
    campo.classList.add("is-invalid");
    const aviso = feedbackDe(campo);
    if (aviso) aviso.textContent = mensaje;
  }

  function limpiarError(campo) {
    campo.classList.remove("is-invalid");
  }

  // Valida un campo y pinta o limpia su estado. Con obligatorio=true mira también
  // si está vacío; en vivo lo llamo con obligatorio=false para no marcar en rojo
  // un campo que aún no se ha rellenado. Devuelve true si es válido.
  function validarCampo(id, obligatorio) {
    const campo = document.getElementById(id);
    if (!campo) return true;
    const valor = campo.value.trim();

    if (obligatorio && OBLIGATORIOS[id] && valor === "") {
      marcarError(campo, OBLIGATORIOS[id]);
      return false;
    }
    const regla = REGLAS[id];
    if (regla && !regla.validar(valor)) {
      marcarError(campo, regla.mensaje);
      return false;
    }
    limpiarError(campo);
    return true;
  }

  // La entrega tiene dos comprobaciones: que no esté vacía y que no sea anterior
  // a la entrada. Las fechas en ISO se comparan como texto (ordenan igual).
  function validarEntrega(obligatorio) {
    if (!entrega) return true;
    const valor = entrega.value.trim();

    if (obligatorio && valor === "") {
      marcarError(entrega, OBLIGATORIOS.fecha_entrega);
      return false;
    }
    if (entrada && entrada.value && valor && valor < entrada.value) {
      marcarError(entrega, "La entrega no puede ser anterior a la entrada.");
      return false;
    }
    limpiarError(entrega);
    return true;
  }

  // Validación en vivo de los campos de formato: al salir del campo (blur) y, si
  // ya está en rojo, en cada tecla (input).
  CAMPOS_FORMATO.forEach(function (id) {
    const campo = document.getElementById(id);
    if (!campo) return;
    campo.addEventListener("blur", function () {
      validarCampo(id, false);
    });
    campo.addEventListener("input", function () {
      if (campo.classList.contains("is-invalid")) validarCampo(id, false);
    });
  });

  // Fechas en vivo: coherencia de la entrega y reajuste del mínimo.
  if (entrega) {
    entrega.addEventListener("blur", function () { validarEntrega(false); });
    entrega.addEventListener("input", function () {
      if (entrega.classList.contains("is-invalid")) validarEntrega(false);
    });
  }
  if (entrada) {
    entrada.addEventListener("change", function () {
      ajustarMinimoEntrega();
      // Si ya había una entrega escrita, la revisamos por si ahora no cuadra.
      if (entrega && entrega.value) validarEntrega(false);
    });
  }

  // Al enviar: compruebo todo (obligatorios + formato + coherencia). Si algo
  // falla, paro el envío y llevo al usuario al primer campo con error.
  formulario.addEventListener("submit", function (evento) {
    let primerError = null;

    function revisar(valido, id) {
      if (!valido && !primerError) {
        primerError = document.getElementById(id);
      }
    }

    revisar(validarCampo("fecha_entrada", true), "fecha_entrada");
    revisar(validarEntrega(true),                "fecha_entrega");
    revisar(validarCampo("nombre", true),        "nombre");
    revisar(validarCampo("marca_modelo", true),  "marca_modelo");
    revisar(validarCampo("matricula", true),     "matricula");
    revisar(validarCampo("telefono", true),      "telefono");
    revisar(validarCampo("cif", true),           "cif");
    revisar(validarCampo("cp", true),            "cp");
    revisar(validarCampo("kilometros", true),    "kilometros");

    if (primerError) {
      evento.preventDefault();
      primerError.scrollIntoView({ behavior: "smooth", block: "center" });
      primerError.focus();
    }
  });

});
