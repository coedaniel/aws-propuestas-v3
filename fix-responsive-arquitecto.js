const fs = require('fs');
const path = require('path');

// Leer el archivo actual
const filePath = path.join(__dirname, 'app/arquitecto/page.tsx');
let content = fs.readFileSync(filePath, 'utf8');

// Aplicar mejoras de responsividad
const improvements = [
  // Header responsivo
  {
    from: 'className="flex items-center justify-between"',
    to: 'className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4"'
  },
  {
    from: 'className="flex items-center space-x-4"',
    to: 'className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4 w-full lg:w-auto"'
  },
  {
    from: 'className="flex items-center space-x-2"',
    to: 'className="flex flex-wrap items-center gap-2"'
  },
  // Botones del header más responsivos
  {
    from: 'size="sm"',
    to: 'size="sm" className="text-xs px-2 py-1 sm:px-3 sm:py-2"'
  },
  // Layout principal responsivo
  {
    from: 'className="flex h-screen"',
    to: 'className="flex flex-col lg:flex-row h-screen"'
  },
  // Panel lateral responsivo
  {
    from: 'className="w-80 border-l border-border bg-card/30 backdrop-blur-sm"',
    to: 'className="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-border bg-card/30 backdrop-blur-sm"'
  },
  // Área de mensajes responsiva
  {
    from: 'className="flex-1 overflow-y-auto p-4 space-y-4"',
    to: 'className="flex-1 overflow-y-auto p-2 sm:p-4 space-y-2 sm:space-y-4"'
  },
  // Burbujas de mensaje responsivas
  {
    from: 'className={`flex space-x-3 max-w-4xl ${isUser ? \'flex-row-reverse space-x-reverse\' : \'\'}`}',
    to: 'className={`flex space-x-2 sm:space-x-3 max-w-full sm:max-w-4xl ${isUser ? \'flex-row-reverse space-x-reverse\' : \'\'}`}'
  },
  // Área de input responsiva
  {
    from: 'className="border-t border-border bg-card/50 backdrop-blur-sm p-4"',
    to: 'className="border-t border-border bg-card/50 backdrop-blur-sm p-2 sm:p-4"'
  },
  {
    from: 'className="flex space-x-4"',
    to: 'className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4"'
  },
  {
    from: 'className="min-h-[80px] resize-none focus-ring"',
    to: 'className="min-h-[60px] sm:min-h-[80px] resize-none focus-ring text-sm sm:text-base"'
  },
  // Botón de envío responsivo
  {
    from: 'className="px-6 self-end"',
    to: 'className="px-4 sm:px-6 w-full sm:w-auto sm:self-end"'
  },
  // Status bar del proyecto responsivo
  {
    from: 'className="mt-4 p-3 bg-muted/30 rounded-lg"',
    to: 'className="mt-2 sm:mt-4 p-2 sm:p-3 bg-muted/30 rounded-lg"'
  },
  {
    from: 'className="flex items-center justify-between"',
    to: 'className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0"'
  }
];

// Aplicar todas las mejoras
improvements.forEach(improvement => {
  content = content.replace(new RegExp(improvement.from, 'g'), improvement.to);
});

// Agregar import del CSS responsivo al inicio del archivo
const importStatement = `import './responsive.css'\n`;
if (!content.includes(importStatement)) {
  content = importStatement + content;
}

// Escribir el archivo mejorado
fs.writeFileSync(filePath, content);

console.log('✅ Mejoras de responsividad aplicadas al componente Arquitecto');
console.log('📱 La página ahora es completamente responsiva');
console.log('🎨 Se agregaron clases Tailwind responsivas');
console.log('📄 Se importó el CSS responsivo personalizado');
