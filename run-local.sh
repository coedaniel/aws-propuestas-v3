#!/bin/bash

echo "🚀 Iniciando AWS Propuestas v3 localmente..."
echo "=================================="

# Verificar Node.js
echo "📋 Verificando Node.js..."
node --version
npm --version

# Verificar dependencias
echo "📦 Verificando dependencias..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  Instalando dependencias..."
    npm install
fi

# Crear archivo .env.local si no existe
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creando archivo .env.local..."
    cp .env.local.example .env.local
    echo "✅ Archivo .env.local creado. Configura tus variables de entorno."
fi

echo ""
echo "🌐 Iniciando servidor de desarrollo..."
echo "📍 URL: http://localhost:3000"
echo "📍 Arquitecto: http://localhost:3000/arquitecto"
echo "📍 Proyectos: http://localhost:3000/proyectos"
echo ""
echo "⏹️  Para detener: Ctrl+C"
echo "=================================="

npm run dev
