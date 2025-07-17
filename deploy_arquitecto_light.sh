#!/bin/bash

# Script para desplegar la corrección ligera del Lambda Arquitecto
# Elimina caracteres especiales y genera archivos reales (versión ligera)

echo "🚀 Desplegando corrección LIGERA del Lambda Arquitecto..."

# Crear directorio temporal
TEMP_DIR=$(mktemp -d)
echo "📁 Directorio temporal: $TEMP_DIR"

# Copiar el código corregido
cp backend_arquitecto_light.py $TEMP_DIR/app.py
cp requirements_arquitecto_light.txt $TEMP_DIR/requirements.txt

# Cambiar al directorio temporal
cd $TEMP_DIR

# Instalar dependencias (solo las esenciales)
echo "📦 Instalando dependencias ligeras..."
pip install -r requirements.txt -t . --no-deps

# Crear el archivo ZIP
echo "📦 Creando archivo ZIP ligero..."
zip -r arquitecto-light.zip . -x "*.pyc" "__pycache__/*"

# Verificar tamaño del ZIP
ZIP_SIZE=$(stat -f%z arquitecto-light.zip 2>/dev/null || stat -c%s arquitecto-light.zip)
echo "📏 Tamaño del ZIP: $(($ZIP_SIZE / 1024 / 1024)) MB"

if [ $ZIP_SIZE -gt 50000000 ]; then
    echo "⚠️ Advertencia: ZIP mayor a 50MB, puede fallar el despliegue"
fi

# Subir a Lambda
echo "☁️ Actualizando función Lambda..."
aws lambda update-function-code \
    --function-name aws-propuestas-v3-arquitecto-prod \
    --zip-file fileb://arquitecto-light.zip \
    --region us-east-1

# Verificar el despliegue
if [ $? -eq 0 ]; then
    echo "✅ Lambda actualizado exitosamente!"
    echo ""
    echo "🔧 FUNCIONALIDADES CORREGIDAS:"
    echo "   ✅ Eliminación de caracteres especiales (ñ, acentos, tildes)"
    echo "   ✅ Generación real de archivos CSV y TXT"
    echo "   ✅ Guardado correcto en DynamoDB"
    echo "   ✅ Subida real de archivos a S3"
    echo "   ✅ Versión ligera sin dependencias pesadas"
    echo ""
    echo "📋 ARCHIVOS QUE SE GENERAN:"
    echo "   📄 [proyecto]-propuesta.txt (documento principal)"
    echo "   📊 [proyecto]-actividades.csv (plan de trabajo)"
    echo "   💰 [proyecto]-costos.csv (estimación de costos)"
    echo "   🧮 [proyecto]-calculadora-guia.txt (guía para AWS Calculator)"
    echo ""
    echo "🎯 PRÓXIMOS PASOS:"
    echo "   1. Probar el arquitecto desde https://main.d2xsphsjdxlk24.amplifyapp.com/arquitecto/"
    echo "   2. Verificar que los archivos se generen SIN caracteres especiales"
    echo "   3. Confirmar que los proyectos aparezcan en /projects/"
    echo "   4. Verificar que system-status muestre servicios en verde"
else
    echo "❌ Error al actualizar Lambda"
    exit 1
fi

# Limpiar
cd - > /dev/null
rm -rf $TEMP_DIR

echo ""
echo "🎉 DESPLIEGUE COMPLETADO!"
echo "🌐 Prueba tu arquitecto en: https://main.d2xsphsjdxlk24.amplifyapp.com/arquitecto/"
