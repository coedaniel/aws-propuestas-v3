#!/bin/bash

# Script para desplegar la corrección del Lambda Arquitecto
# Elimina caracteres especiales y genera archivos reales

echo "🚀 Desplegando corrección del Lambda Arquitecto..."

# Crear directorio temporal
TEMP_DIR=$(mktemp -d)
echo "📁 Directorio temporal: $TEMP_DIR"

# Copiar el código corregido
cp backend_arquitecto_fixed.py $TEMP_DIR/app.py
cp requirements_arquitecto.txt $TEMP_DIR/requirements.txt

# Cambiar al directorio temporal
cd $TEMP_DIR

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt -t .

# Crear el archivo ZIP
echo "📦 Creando archivo ZIP..."
zip -r arquitecto-fixed.zip . -x "*.pyc" "__pycache__/*"

# Subir a Lambda
echo "☁️ Actualizando función Lambda..."
aws lambda update-function-code \
    --function-name aws-propuestas-v3-arquitecto-prod \
    --zip-file fileb://arquitecto-fixed.zip \
    --region us-east-1

# Verificar el despliegue
if [ $? -eq 0 ]; then
    echo "✅ Lambda actualizado exitosamente!"
    echo "🔧 Funcionalidades corregidas:"
    echo "   - Eliminación de caracteres especiales (ñ, acentos, tildes)"
    echo "   - Generación real de archivos CSV, DOCX"
    echo "   - Guardado correcto en DynamoDB"
    echo "   - Subida real de archivos a S3"
    echo ""
    echo "📋 Próximos pasos:"
    echo "   1. Probar el arquitecto desde la web"
    echo "   2. Verificar que los archivos se generen sin caracteres especiales"
    echo "   3. Confirmar que los proyectos aparezcan en la página de proyectos"
else
    echo "❌ Error al actualizar Lambda"
    exit 1
fi

# Limpiar
cd - > /dev/null
rm -rf $TEMP_DIR

echo "🎉 Despliegue completado!"
