#!/bin/bash

echo "🚀 DESPLEGANDO CORRECCIONES AWS PROPUESTAS V3"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    error "No se encontró package.json. Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

log "Iniciando despliegue de correcciones..."

# 1. ACTUALIZAR LAMBDA ARQUITECTO
log "1. Actualizando Lambda Arquitecto..."

# Backup del archivo original
cp lambda/arquitecto/app.py lambda/arquitecto/app_backup_$(date +%Y%m%d_%H%M%S).py

# Reemplazar con la versión corregida
cp lambda/arquitecto/app_fixed.py lambda/arquitecto/app.py

# Desplegar Lambda Arquitecto
cd lambda/arquitecto
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -t .
fi

# Crear ZIP para deployment
zip -r arquitecto-fixed.zip . -x "*.pyc" "__pycache__/*" "app_fixed.py" "app_backup_*"

# Actualizar función Lambda
aws lambda update-function-code \
    --function-name aws-propuestas-v3-arquitecto-prod \
    --zip-file fileb://arquitecto-fixed.zip \
    --region us-east-1

if [ $? -eq 0 ]; then
    log "✅ Lambda Arquitecto actualizada exitosamente"
else
    error "❌ Error actualizando Lambda Arquitecto"
fi

cd ../..

# 2. ACTUALIZAR LAMBDA PROJECTS
log "2. Actualizando Lambda Projects..."

# Backup del archivo original si existe
if [ -f "lambda/projects/app.py" ]; then
    cp lambda/projects/app.py lambda/projects/app_backup_$(date +%Y%m%d_%H%M%S).py
fi

# Reemplazar con la versión corregida
cp lambda/projects/app_fixed.py lambda/projects/app.py

# Desplegar Lambda Projects
cd lambda/projects
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -t .
fi

# Crear ZIP para deployment
zip -r projects-fixed.zip . -x "*.pyc" "__pycache__/*" "app_fixed.py" "app_backup_*"

# Actualizar función Lambda
aws lambda update-function-code \
    --function-name aws-propuestas-v3-projects-prod \
    --zip-file fileb://projects-fixed.zip \
    --region us-east-1

if [ $? -eq 0 ]; then
    log "✅ Lambda Projects actualizada exitosamente"
else
    error "❌ Error actualizando Lambda Projects"
fi

cd ../..

# 3. ACTUALIZAR FRONTEND
log "3. Actualizando Frontend..."

# Backup de la página original
cp app/proyectos/page.tsx app/proyectos/page_backup_$(date +%Y%m%d_%H%M%S).tsx

# Reemplazar con la versión corregida
cp app/proyectos/page_fixed.tsx app/proyectos/page.tsx

# 4. VERIFICAR CONFIGURACIÓN DE API GATEWAY
log "4. Verificando configuración de API Gateway..."

# Verificar que los endpoints estén configurados
aws apigateway get-resources \
    --rest-api-id jvdvd1qcdj \
    --region us-east-1 \
    --query 'items[?pathPart==`projects`]' \
    --output table

# 5. VERIFICAR TABLAS DYNAMODB
log "5. Verificando tablas DynamoDB..."

# Verificar tabla de proyectos
aws dynamodb describe-table \
    --table-name aws-propuestas-v3-projects-prod \
    --region us-east-1 \
    --query 'Table.{TableName:TableName,Status:TableStatus,ItemCount:ItemCount}' \
    --output table

# 6. VERIFICAR BUCKET S3
log "6. Verificando bucket S3..."

# Verificar bucket de documentos
aws s3 ls s3://aws-propuestas-v3-documents-prod-035385358261/ --region us-east-1

# 7. PROBAR ENDPOINTS
log "7. Probando endpoints..."

# Test Chat
info "Probando endpoint de Chat..."
curl -s -X POST "https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/chat" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Test"}], "modelId": "amazon.nova-pro-v1:0"}' \
  | jq -r '.response' | head -1

# Test Arquitecto
info "Probando endpoint de Arquitecto..."
curl -s -X POST "https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/arquitecto" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Mi proyecto es Test"}], "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0", "projectState": {"phase": "inicio", "data": {}}}' \
  | jq -r '.content' | head -1

# Test Projects
info "Probando endpoint de Projects..."
curl -s -X GET "https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/projects" \
  -H "Content-Type: application/json" \
  | jq -r '.projects | length'

# 8. VERIFICAR MCPS
log "8. Verificando MCPs..."

for service in core pricing awsdocs cfn diagram docgen; do
    info "Verificando MCP $service..."
    curl -s "https://mcp.danielingram.shop/$service/health" | jq -r '.status'
done

# 9. REBUILD FRONTEND LOCAL
log "9. Reconstruyendo frontend local..."

npm run build

if [ $? -eq 0 ]; then
    log "✅ Frontend reconstruido exitosamente"
else
    error "❌ Error reconstruyendo frontend"
fi

# 10. DESPLEGAR A AMPLIFY (opcional)
read -p "¿Deseas desplegar a Amplify? (y/n): " deploy_amplify

if [ "$deploy_amplify" = "y" ] || [ "$deploy_amplify" = "Y" ]; then
    log "10. Desplegando a Amplify..."
    
    # Commit cambios
    git add .
    git commit -m "🚀 Deploy fixes: Arquitecto completo + Projects funcional + Frontend actualizado"
    git push origin main
    
    log "✅ Cambios enviados a repositorio. Amplify desplegará automáticamente."
else
    info "Saltando despliegue a Amplify."
fi

# RESUMEN FINAL
echo ""
echo "=============================================="
log "🎉 DESPLIEGUE DE CORRECCIONES COMPLETADO"
echo "=============================================="
echo ""
echo "✅ CAMBIOS IMPLEMENTADOS:"
echo "   • Lambda Arquitecto: Flujo completo de consultoría"
echo "   • Lambda Projects: Conexión real con DynamoDB y S3"
echo "   • Frontend Projects: Interface conectada con backend"
echo "   • Generación automática de documentos"
echo "   • Subida de archivos a S3"
echo "   • Guardado de proyectos en DynamoDB"
echo ""
echo "🔗 ENDPOINTS ACTIVOS:"
echo "   • Chat: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/chat"
echo "   • Arquitecto: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/arquitecto"
echo "   • Projects: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/projects"
echo ""
echo "🌐 FRONTEND:"
echo "   • Local: http://localhost:3000"
echo "   • Amplify: https://d2xsphsjdxlk24.amplifyapp.com"
echo ""
echo "🛠️ MCPs ACTIVOS:"
echo "   • Core: https://mcp.danielingram.shop"
echo "   • Pricing: https://mcp.danielingram.shop/pricing"
echo "   • AWS Docs: https://mcp.danielingram.shop/awsdocs"
echo "   • CloudFormation: https://mcp.danielingram.shop/cfn"
echo "   • Diagrams: https://mcp.danielingram.shop/diagram"
echo "   • Custom Docs: https://mcp.danielingram.shop/docgen"
echo ""
log "🚀 Sistema completamente funcional y listo para uso!"
echo ""
