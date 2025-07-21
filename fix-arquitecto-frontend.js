// Corrección para el problema de recarga de página en arquitecto
// Este script debe ser ejecutado en la consola del navegador como workaround temporal

console.log('🔧 Aplicando corrección temporal para arquitecto...');

// Prevenir que los formularios se envíen y recarguen la página
document.addEventListener('submit', function(e) {
    e.preventDefault();
    console.log('Form submission prevented');
});

// Prevenir que Enter recargue la página en textareas
document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        
        // Buscar el botón de envío y hacer click
        const sendButton = document.querySelector('button[type="button"]:not([disabled])');
        if (sendButton && sendButton.textContent === '') {
            // Es el botón con el ícono de envío
            sendButton.click();
        }
    }
});

console.log('✅ Corrección aplicada. Ahora prueba escribir un mensaje.');
