/* ===========================================================================
   Autorrelleno del formulario por matrícula.

   Cuando se escribe una matrícula ya registrada, le pido al servidor
   (/incidencias/matricula/<matricula>) los datos del cliente y del vehículo y
   relleno esos campos solos, así no hay que teclearlos otra vez. Los datos de
   ESTA visita (fechas, km, combustible, reparaciones) no se tocan.
   =========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  const matricula = document.getElementById("matricula");
  if (!matricula) return;   // si no estamos en el formulario, no hacemos nada

  // Campos que se rellenan con lo que devuelve el servidor. El id de cada input
  // coincide con el nombre del dato en el JSON, así el relleno es directo.
  const CAMPOS = ["nombre", "cif", "telefono", "domicilio",
                  "numero", "cp", "poblacion", "marca_modelo"];

  // Aviso bajo la matrícula cuando recupero datos. Lo creo una vez y lo
  // muestro u oculto según haga falta.
  const aviso = document.createElement("div");
  aviso.className = "form-text text-success";
  aviso.style.display = "none";
  matricula.insertAdjacentElement("afterend", aviso);

  // Uso "change" (salta al salir del campo o con Tab) en vez de "input", para
  // no llamar al servidor con cada tecla.
  matricula.addEventListener("change", autorrellenar);

  async function autorrellenar() {
    // Normalizo igual que el servidor: mayúsculas, sin guiones ni espacios.
    const valor = matricula.value.toUpperCase().replace(/[-\s]/g, "");

    // Solo pregunto si parece una matrícula completa (6-8 caracteres), para no
    // hacer llamadas inútiles con el campo a medias.
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
      // Si el servidor no responde, no rompo nada: se rellena a mano.
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
