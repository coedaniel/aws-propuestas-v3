#!/bin/bash

echo "🧹 Iniciando limpieza de archivos obsoletos..."
echo "📊 Estado inicial del repositorio:"
echo "   Archivos totales: $(find . -type f | wc -l)"
echo "   Tamaño del repo: $(du -sh . | cut -f1)"

# Contador de archivos eliminados
deleted_count=0

# Función para eliminar archivo si existe
safe_delete() {
    if [ -f "$1" ]; then
        rm -f "$1"
        echo "   ❌ Eliminado: $1"
        ((deleted_count++))
    fi
}

# Función para eliminar directorio si existe
safe_delete_dir() {
    if [ -d "$1" ]; then
        rm -rf "$1"
        echo "   ❌ Eliminado directorio: $1"
        ((deleted_count++))
    fi
}

echo ""
echo "🗑️  Eliminando archivos obsoletos del Lambda..."

# Lambda - Versiones obsoletas
safe_delete "lambda/arquitecto/app_backup_20250721-214629.py"
safe_delete "lambda/arquitecto/app_backup_before_intelligent.py"
safe_delete "lambda/arquitecto/app_broken.py"
safe_delete "lambda/arquitecto/backend_arquitecto_contenedor.py"
safe_delete "lambda/arquitecto/backend_arquitecto_final.py"
safe_delete "lambda/arquitecto/backend_arquitecto_fix.py"
safe_delete "lambda/arquitecto/backend_arquitecto_guiado.py"
safe_delete "lambda/arquitecto/backend_arquitecto_maestro.py"
safe_delete "lambda/arquitecto/backend_arquitecto_mcp_real.py"
safe_delete "lambda/arquitecto/backend_arquitecto_mcp_simple.py"
safe_delete "lambda/arquitecto/backend_arquitecto_real.py"
safe_delete "lambda/arquitecto/backend_arquitecto_simple.py"
safe_delete "lambda/arquitecto/mcp_orchestrator.py"
safe_delete "lambda/arquitecto/smart_mcp_handler.py"
safe_delete "lambda/arquitecto/document_generator.py"
safe_delete "lambda/arquitecto/test_mcp_connectivity.py"

echo ""
echo "🗑️  Eliminando archivos obsoletos del Frontend..."

# Frontend - Páginas obsoletas
safe_delete "app/arquitecto/page-broken.tsx"
safe_delete "app/arquitecto/page-old.tsx"

# Buscar y eliminar backups del arquitecto
for file in app/arquitecto/page-backup-*.tsx; do
    if [ -f "$file" ]; then
        safe_delete "$file"
    fi
done

echo ""
echo "🗑️  Eliminando scripts obsoletos..."

# Scripts obsoletos
safe_delete "fix-responsive-arquitecto.js"
safe_delete "fix-arquitecto-frontend.js"
safe_delete "deploy-arquitecto-fix.sh"

# Scripts de deploy antiguos
for file in deploy-v2*.sh; do
    if [ -f "$file" ]; then
        safe_delete "$file"
    fi
done

# Scripts de cleanup antiguos (excepto este)
for file in cleanup_*.sh; do
    if [ -f "$file" ] && [ "$file" != "cleanup_obsolete_files.sh" ]; then
        safe_delete "$file"
    fi
done

echo ""
echo "🗑️  Eliminando documentación obsoleta..."

# Documentación obsoleta
safe_delete "CURRENT_STATUS.md"
safe_delete "SYSTEM_STATUS.md"
safe_delete "DEPLOYMENT_READY.md"
safe_delete "DEPLOYMENT_SUMMARY.md"

# Build logs
for file in build_log*.txt; do
    if [ -f "$file" ]; then
        safe_delete "$file"
    fi
done

echo ""
echo "🗑️  Eliminando archivos ZIP antiguos..."

# Mantener solo los 2 ZIPs más recientes en lambda/arquitecto
cd lambda/arquitecto/
if ls arquitecto-*.zip 1> /dev/null 2>&1; then
    # Contar archivos ZIP
    zip_count=$(ls -1 arquitecto-*.zip | wc -l)
    if [ $zip_count -gt 2 ]; then
        # Eliminar todos excepto los 2 más recientes
        ls -t arquitecto-*.zip | tail -n +3 | while read file; do
            rm -f "$file"
            echo "   ❌ Eliminado ZIP antiguo: lambda/arquitecto/$file"
            ((deleted_count++))
        done
    fi
fi
cd ../../

echo ""
echo "🗑️  Eliminando configuraciones obsoletas..."

# Configuraciones MCP obsoletas
safe_delete "core-mcp-task-def-cors.json"
safe_delete "diagram-mcp-task-def-cors-fixed.json"
safe_delete "diagram-mcp-task-def-cors.json"

# Dockerfiles obsoletos
for file in Dockerfile.*-fixed; do
    if [ -f "$file" ]; then
        safe_delete "$file"
    fi
done

echo ""
echo "🗑️  Eliminando archivos temporales y de desarrollo..."

# Archivos temporales
safe_delete "=0.2.6"
safe_delete "test-payload.json"
safe_delete "response*.json"
safe_delete "test-*.json"
safe_delete "test-*.html"

# Archivos de configuración obsoletos
safe_delete "next.config.js"  # Si existe uno obsoleto en root

# Backups de GitHub
safe_delete_dir "aws-propuestas-v3-github-BACKUP-*"
safe_delete_dir "aws-propuestas-v3-backup-*"
safe_delete_dir "aws-propuestas-v3-simplified-backup-*"

echo ""
echo "🗑️  Eliminando archivos de otros proyectos..."

# Archivos de otros proyectos que no pertenecen aquí
safe_delete_dir "aws-spd-guide"
safe_delete_dir "spd-waf"
safe_delete_dir "bedrock-chat-app"
safe_delete_dir "bedrock-chat-interface"
safe_delete_dir "bedrock-chat-interface-secure"
safe_delete_dir "bedrock-proxy-lambda"

# Archivos ZIP de otros proyectos
safe_delete "bedrock-chat-app.zip"
safe_delete "transformbridge-*.zip"
safe_delete "simple-*.zip"

echo ""
echo "✅ Limpieza completada!"
echo ""
echo "📊 Resumen de la limpieza:"
echo "   Archivos eliminados: $deleted_count"
echo "   Archivos restantes: $(find . -type f | wc -l)"
echo "   Nuevo tamaño del repo: $(du -sh . | cut -f1)"
echo ""
echo "🎯 Archivos IMPORTANTES mantenidos:"
echo "   ✅ lambda/arquitecto/app.py (Lambda principal)"
echo "   ✅ lambda/arquitecto/intelligent_mcp_orchestrator.py"
echo "   ✅ lambda/arquitecto/cors_handler.py"
echo "   ✅ app/arquitecto/page.tsx (Frontend principal)"
echo "   ✅ app/arquitecto/responsive.css"
echo "   ✅ official-mcp-servers/ (6 MCPs oficiales)"
echo "   ✅ docs/ (Documentación actualizada)"
echo "   ✅ README.md (Documentación principal)"
echo ""
echo "🚀 Repositorio optimizado para producción!"
echo ""
echo "📋 Próximos pasos recomendados:"
echo "   1. git add ."
echo "   2. git commit -m '🧹 CLEANUP: Remove obsolete files'"
echo "   3. git push origin main"
echo "   4. Verificar que la aplicación sigue funcionando"
echo ""
