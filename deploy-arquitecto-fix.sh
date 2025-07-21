#!/bin/bash

echo "🚀 Desplegando corrección de Lambda Arquitecto..."
echo "================================================"

# Navegar al directorio de la lambda
cd lambda/arquitecto

# Crear el paquete de deployment
echo "📦 Creando paquete de deployment..."
zip -r arquitecto-fix.zip . -x "__pycache__/*" "*.pyc" "test_*" "*.zip"

# Actualizar la función Lambda
echo "🔄 Actualizando función Lambda..."
aws lambda update-function-code \
    --function-name aws-propuestas-v3-arquitecto-prod \
    --zip-file fileb://arquitecto-fix.zip \
    --region us-east-1

if [ $? -eq 0 ]; then
    echo "✅ Lambda actualizada exitosamente!"
    
    # Esperar a que la función esté lista
    echo "⏳ Esperando a que la función esté lista..."
    aws lambda wait function-updated \
        --function-name aws-propuestas-v3-arquitecto-prod \
        --region us-east-1
    
    echo "🧪 Ejecutando test de conectividad..."
    python3 ../../test_arquitecto_complete.py
    
else
    echo "❌ Error al actualizar la Lambda"
    exit 1
fi

echo "🎯 Deployment completado!"
