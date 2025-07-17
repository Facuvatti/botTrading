function deleteElement(selector) {
  const elemento = document.querySelector(selector);
  if (elemento) {
    elemento.remove(); // Elimina el elemento si lo encuentra
    console.log(`Elemento con selector "${selector}" eliminado.`);
  } else {
    console.log(`No se encontró ningún elemento con el selector "${selector}".`);
  }
}
function scriptWithDelay(type, content, delayMs) {
  setTimeout(() => {
    const script = document.createElement('script');

    if (type === 'inline') {
      // Si es código JavaScript directo
      script.textContent = content;
      console.log('Se agregará un script con código inline.');
    } else if (type === 'src') {
      // Si es una URL de un archivo JavaScript
      script.src = content;
      console.log(`Se agregará un script desde la URL: ${content}`);
    } else {
      console.error('Tipo de script no válido. Use "inline" o "src".');
      return;
    }

    // Opcional: Para scripts externos, puedes agregar un evento para saber cuándo cargó
    script.onload = () => {
      console.log('El script se ha cargado y ejecutado.');
    };
    script.onerror = () => {
      console.error('Error al cargar el script.');
    };

    // Añade el script al final del body
    // Es común añadir scripts al final del <body> para no bloquear el renderizado inicial.
    document.body.appendChild(script);

  }, delayMs);
}
const check = document.getElementById('check')
const mainContent = document.querySelector('.main-content')
// Añade el event listener para detectar cuando cambia el checkbox
check.addEventListener('change', function() {
  // Si está marcado, cambia el margen de .main-content
  if (check.checked) {
    mainContent.style.marginLeft = '330px';
  } else {
    mainContent.style.marginLeft = '0px';
  }
});

scriptWithDelay("inline", 'deleteElement("#tv-attr-logo");', 41);

