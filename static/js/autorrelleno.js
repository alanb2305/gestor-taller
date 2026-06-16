/* ===========================================================================
   Autorrelleno del formulario por matrícula.

   Cuando el usuario escribe una matrícula que ya está registrada, le pedimos
   al servidor (endpoint /incidencias/matricula/<matricula>) los datos del
   cliente y del vehículo y rellenamos esos campos solos. Así no hay que
   volver a teclear los datos de un cliente que ya ha venido otras veces.

   Los datos propios de ESTA visita (fechas, kilómetros, combustible y
   reparaciones) no se tocan: cambian en cada entrada al taller.
   =========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  const matricula = document.getElementById("matricula");
  if (!matricula) return;   // si no estamos en el formulario, no hacemos nada

  // Campos que se rellenan con lo que devuelve el servidor. El id de cada
  // <input> coincide a propósito con el nombre del dato en el JSON, así el
  // relleno es directo (campo.value = datos[id]).
  const CAMPOS = ["nombre", "cif", "telefono", "domicilio",
                  "numero", "cp", "poblacion", "marca_modelo"];

  // Aviso que aparece bajo la matrícula cuando recuperamos datos. Lo creamos
  // una sola vez y lo mostramos u ocultamos según haga falta.
  const aviso = document.createElement("div");
  aviso.className = "form-text text-success";
  aviso.style.display = "none";
  matricula.insertAdjacentElement("afterend", aviso);

  // Usamos "change" (salta al salir del campo o pulsar Tab) en lugar de
  // "input", para no llamar al servidor con cada tecla mientras se escribe.
  matricula.addEventListener("change", autorrellenar);

  async function autorrellenar() {
    // Normalizamos igual que el servidor: mayúsculas, sin guiones ni espacios.
    const valor = matricula.value.toUpperCase().replace(/[-\s]/g, "");

    // Solo preguntamos si parece una matrícula completa (entre 6 y 8
    // caracteres). El formato exacto ya lo comprueban validaciones.js y el
    // servidor; aquí solo evitamos llamadas inútiles con el campo a medias.
    if (valor.length < 6 || valor.length > 8) {
      ocultarAviso();
      return;
    }

    try {
      const respuesta = await fetch(`/incidencias/matricula/${valor}`);
      const datos = await respuesta.json();

      if (datos.encontrado) {
        rellenar(datos);
        mostrarAviso("Datos recuperados de una ficha anterior. " +
                     "Revisa que sigan siendo correctos.");
      } else {
        ocultarAviso();   // matrícula nueva: no tocamos nada
      }
    } catch (error) {
      // Si el servidor no responde, no rompemos el formulario: el usuario
      // siempre puede rellenar los campos a mano.
      console.error("No se pudo consultar la matrícula:", error);
    }
  }

  function rellenar(datos) {
    CAMPOS.forEach(function (id) {
      const campo = document.getElementById(id);
      if (campo) {
        campo.value = datos[id] || "";
      }
    });
  }

  function mostrarAviso(texto) {
    aviso.textContent = texto;
    aviso.style.display = "block";
  }

  function ocultarAviso() {
    aviso.style.display = "none";
  }

});
