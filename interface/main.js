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
