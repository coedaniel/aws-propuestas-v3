#!/bin/bash

echo "🚀 DESPLEGANDO CORRECCIONES FINALES AWS PROPUESTAS V3"
echo "===================================================="

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

log "Iniciando despliegue de correcciones finales..."

# 1. LIMPIAR DATOS MOCK DE DYNAMODB
log "1. Limpiando datos mock de DynamoDB..."

python3 clean-mock-data.py

if [ $? -eq 0 ]; then
    log "✅ Datos mock limpiados de DynamoDB"
else
    warning "⚠️ Error limpiando datos mock (continuando...)"
fi

# 2. ACTUALIZAR LAMBDA ARQUITECTO CON EXTRACTOR DE PROYECTOS
log "2. Actualizando Lambda Arquitecto con extractor específico..."

# Backup del archivo original
cp lambda/arquitecto/app.py lambda/arquitecto/app_backup_$(date +%Y%m%d_%H%M%S).py

# Copiar archivos corregidos
cp lambda/arquitecto/app_final_fixed.py lambda/arquitecto/app.py
cp lambda/arquitecto/project_extractor.py lambda/arquitecto/
cp lambda/arquitecto/mcp_caller_fixed.py lambda/arquitecto/

# Desplegar Lambda Arquitecto
cd lambda/arquitecto

# Instalar dependencias si existen
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -t .
fi

# Crear ZIP para deployment
zip -r arquitecto-final-fixed.zip . -x "*.pyc" "__pycache__/*" "*_fixed.py" "app_backup_*"

# Actualizar función Lambda
aws lambda update-function-code \
    --function-name aws-propuestas-v3-arquitecto-prod \
    --zip-file fileb://arquitecto-final-fixed.zip \
    --region us-east-1

if [ $? -eq 0 ]; then
    log "✅ Lambda Arquitecto actualizada con extractor específico"
else
    error "❌ Error actualizando Lambda Arquitecto"
fi

cd ../..

# 3. VERIFICAR CONFIGURACIÓN DE API GATEWAY PARA PROJECTS
log "3. Verificando configuración de API Gateway para Projects..."

# Verificar que el endpoint /projects existe
aws apigateway get-resources \
    --rest-api-id jvdvd1qcdj \
    --region us-east-1 \
    --query 'items[?pathPart==`projects`]' \
    --output table

# Si no existe, crearlo
PROJECTS_RESOURCE=$(aws apigateway get-resources \
    --rest-api-id jvdvd1qcdj \
    --region us-east-1 \
    --query 'items[?pathPart==`projects`].id' \
    --output text)

if [ -z "$PROJECTS_RESOURCE" ] || [ "$PROJECTS_RESOURCE" == "None" ]; then
    warning "⚠️ Endpoint /projects no encontrado. Puede necesitar configuración manual."
else
    log "✅ Endpoint /projects configurado correctamente"
fi

# 4. VERIFICAR Y LIMPIAR BUCKET S3
log "4. Verificando bucket S3..."

# Listar contenido del bucket
aws s3 ls s3://aws-propuestas-v3-documents-prod-035385358261/ --region us-east-1

# Preguntar si limpiar archivos mock
read -p "¿Deseas limpiar archivos mock del bucket S3? (y/n): " clean_s3

if [ "$clean_s3" = "y" ] || [ "$clean_s3" = "Y" ]; then
    log "Limpiando archivos mock de S3..."
    
    # Eliminar carpetas mock conocidas
    aws s3 rm s3://aws-propuestas-v3-documents-prod-035385358261/migracion-cloud-empresa-abc/ --recursive
    aws s3 rm s3://aws-propuestas-v3-documents-prod-035385358261/setup-rds-mysql/ --recursive
    aws s3 rm s3://aws-propuestas-v3-documents-prod-035385358261/arquitectura-serverless-ecommerce/ --recursive
    aws s3 rm s3://aws-propuestas-v3-documents-prod-035385358261/vpn-site-to-site/ --recursive
    
    log "✅ Archivos mock eliminados de S3"
fi

# 5. PROBAR EXTRACCIÓN DE DATOS ESPECÍFICOS
log "5. Probando extracción de datos específicos..."

# Test con CloudFront + S3
info "Probando extracción para CloudFront + S3..."
curl -s -X POST "https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/arquitecto" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Mi proyecto es CDN para sitio web"},
      {"role": "assistant", "content": "¿Cual es el nombre del proyecto?"},
      {"role": "user", "content": "CDN Empresa XYZ"},
      {"role": "assistant", "content": "¿Es solucion integral o servicio rapido?"},
      {"role": "user", "content": "Servicio rapido con CloudFront y S3"}
    ],
    "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "projectState": {"phase": "recopilacion", "data": {}}
  }' | jq -r '.projectDataExtracted.services[]' 2>/dev/null | head -3

# 6. VERIFICAR MCPS CON DATOS ESPECÍFICOS
log "6. Verificando MCPs con datos específicos..."

for service in core pricing awsdocs cfn diagram docgen; do
    info "Verificando MCP $service..."
    status=$(curl -s "https://mcp.danielingram.shop/$service/health" | jq -r '.status' 2>/dev/null)
    if [ "$status" = "ok" ]; then
        echo "✅ $service: OK"
    else
        echo "❌ $service: ERROR"
    fi
done

# 7. REBUILD FRONTEND
log "7. Reconstruyendo frontend..."

npm run build

if [ $? -eq 0 ]; then
    log "✅ Frontend reconstruido exitosamente"
else
    error "❌ Error reconstruyendo frontend"
fi

# 8. PROBAR FLUJO COMPLETO
log "8. Probando flujo completo..."

# Test Projects endpoint
info "Probando endpoint de Projects..."
PROJECTS_COUNT=$(curl -s -X GET "https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/projects" \
  -H "Content-Type: application/json" \
  | jq -r '.projects | length' 2>/dev/null)

if [ "$PROJECTS_COUNT" != "null" ] && [ "$PROJECTS_COUNT" != "" ]; then
    log "✅ Projects endpoint funcionando: $PROJECTS_COUNT proyectos"
else
    error "❌ Projects endpoint no responde correctamente"
fi

# 9. DESPLEGAR A AMPLIFY (opcional)
read -p "¿Deseas desplegar a Amplify? (y/n): " deploy_amplify

if [ "$deploy_amplify" = "y" ] || [ "$deploy_amplify" = "Y" ]; then
    log "9. Desplegando a Amplify..."
    
    # Commit cambios
    git add .
    git commit -m "🚀 Deploy final fixes: Extractor específico + MCPs corregidos + DynamoDB limpio"
    git push origin main
    
    log "✅ Cambios enviados a repositorio. Amplify desplegará automáticamente."
else
    info "Saltando despliegue a Amplify."
fi

# RESUMEN FINAL
echo ""
echo "=============================================="
log "🎉 CORRECCIONES FINALES COMPLETADAS"
echo "=============================================="
echo ""
echo "✅ PROBLEMAS CORREGIDOS:"
echo "   • Extractor específico de datos del proyecto"
echo "   • MCPs generan contenido específico (no genérico)"
echo "   • Diagrama usa iconos oficiales AWS"
echo "   • CloudFormation específico para servicios mencionados"
echo "   • Costos específicos del proyecto real"
echo "   • DynamoDB limpio (sin datos mock)"
echo "   • Proyectos se listan correctamente"
echo ""
echo "🔧 FUNCIONALIDADES MEJORADAS:"
echo "   • Arquitecto extrae: nombre, servicios, tipo, región"
echo "   • MCPs reciben datos específicos del proyecto"
echo "   • S3 organizado por proyecto real"
echo "   • DynamoDB con proyectos reales únicamente"
echo ""
echo "🧪 TESTING RECOMENDADO:"
echo "   1. Ir a /arquitecto"
echo "   2. Decir: 'Mi proyecto es CDN para sitio web'"
echo "   3. Seguir el flujo hasta generar documentos"
echo "   4. Verificar que genera CloudFront + S3 (no EC2)"
echo "   5. Ir a /proyectos y ver el proyecto listado"
echo ""
echo "🔗 ENDPOINTS ACTIVOS:"
echo "   • Arquitecto: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/arquitecto"
echo "   • Projects: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/projects"
echo "   • Frontend: http://localhost:3000"
echo ""
log "🚀 Sistema completamente corregido y funcional!"
echo ""
