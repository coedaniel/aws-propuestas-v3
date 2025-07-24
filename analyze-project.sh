#!/bin/bash

echo "🔍 ANÁLISIS COMPLETO - AWS Propuestas v3"
echo "========================================"
echo ""

# Información del proyecto
echo "📊 INFORMACIÓN DEL PROYECTO"
echo "----------------------------"
echo "📁 Directorio: $(pwd)"
echo "🌐 Repositorio: https://github.com/coedaniel/aws-propuestas-v3"
echo "🚀 Producción: https://main.d2xsphsjdxlk24.amplifyapp.com/"
echo ""

# Estado de Git
echo "📋 ESTADO DEL REPOSITORIO"
echo "-------------------------"
echo "🌿 Branch actual: $(git branch --show-current)"
echo "📝 Último commit: $(git log --oneline -1)"
echo "🔄 Estado: $(git status --porcelain | wc -l) archivos modificados"
echo ""

# Información de Node.js
echo "⚙️ ENTORNO DE DESARROLLO"
echo "------------------------"
echo "📦 Node.js: $(node --version)"
echo "📦 npm: $(npm --version)"
echo "📦 Next.js: $(npm list next --depth=0 2>/dev/null | grep next | cut -d'@' -f2)"
echo ""

# Dependencias
echo "📚 DEPENDENCIAS PRINCIPALES"
echo "---------------------------"
echo "⚛️ React: $(npm list react --depth=0 2>/dev/null | grep react | cut -d'@' -f2)"
echo "🎨 Tailwind: $(npm list tailwindcss --depth=0 2>/dev/null | grep tailwindcss | cut -d'@' -f2)"
echo "📝 TypeScript: $(npm list typescript --depth=0 2>/dev/null | grep typescript | cut -d'@' -f2)"
echo "🧩 Radix UI: $(npm list @radix-ui/react-dialog --depth=0 2>/dev/null | grep react-dialog | cut -d'@' -f3)"
echo ""

# Estructura del proyecto
echo "📁 ESTRUCTURA DEL PROYECTO"
echo "--------------------------"
echo "📱 Frontend:"
find app -name "*.tsx" -o -name "*.ts" | head -10 | sed 's/^/   ├── /'
echo "🧩 Componentes:"
find components -name "*.tsx" -o -name "*.ts" | head -5 | sed 's/^/   ├── /'
echo "🚀 Backend:"
find lambda -name "*.py" | head -5 | sed 's/^/   ├── /'
echo ""

# URLs disponibles
echo "🌐 URLS DISPONIBLES"
echo "-------------------"
echo "🏠 Local Dashboard: http://localhost:3000"
echo "🤖 Local Arquitecto: http://localhost:3000/arquitecto"
echo "📁 Local Proyectos: http://localhost:3000/proyectos"
echo "💬 Local Chat: http://localhost:3000/chat"
echo ""
echo "🌍 Prod Dashboard: https://main.d2xsphsjdxlk24.amplifyapp.com/"
echo "🤖 Prod Arquitecto: https://main.d2xsphsjdxlk24.amplifyapp.com/arquitecto/"
echo "📁 Prod Proyectos: https://main.d2xsphsjdxlk24.amplifyapp.com/proyectos/"
echo ""

# Estado del servidor
echo "🚀 ESTADO DEL SERVIDOR"
echo "----------------------"
if pgrep -f "next dev" > /dev/null; then
    echo "✅ Servidor Next.js: CORRIENDO"
    echo "📍 PID: $(pgrep -f "next dev")"
    echo "🌐 URL: http://localhost:3000"
else
    echo "❌ Servidor Next.js: DETENIDO"
    echo "💡 Para iniciar: npm run dev"
fi
echo ""

# Archivos de configuración
echo "⚙️ CONFIGURACIÓN"
echo "----------------"
if [ -f ".env.local" ]; then
    echo "✅ .env.local: CONFIGURADO"
else
    echo "❌ .env.local: NO ENCONTRADO"
    echo "💡 Copiar desde: .env.local.example"
fi

if [ -f "package.json" ]; then
    echo "✅ package.json: OK"
else
    echo "❌ package.json: NO ENCONTRADO"
fi

if [ -f "template.yaml" ]; then
    echo "✅ template.yaml (SAM): OK"
else
    echo "❌ template.yaml: NO ENCONTRADO"
fi
echo ""

# Comandos útiles
echo "🛠️ COMANDOS ÚTILES"
echo "------------------"
echo "🚀 Iniciar desarrollo: npm run dev"
echo "🏗️ Build producción: npm run build"
echo "🧹 Linter: npm run lint"
echo "📤 Export estático: npm run export"
echo "🔄 Git status: git status"
echo "📤 Git push: git push origin main"
echo ""

# Próximos pasos
echo "📋 PRÓXIMOS PASOS RECOMENDADOS"
echo "------------------------------"
echo "1. 🚀 Iniciar servidor: ./run-local.sh"
echo "2. 🌐 Abrir navegador: http://localhost:3000"
echo "3. 🤖 Probar Arquitecto: http://localhost:3000/arquitecto"
echo "4. 📁 Ver Proyectos: http://localhost:3000/proyectos"
echo "5. 🔧 Personalizar: Editar archivos en app/"
echo ""

echo "✨ ¡Proyecto listo para desarrollo!"
echo "========================================"
