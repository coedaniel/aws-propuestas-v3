#!/bin/bash

echo "🔍 Verificando estado del despliegue..."

STACK_NAME="aws-propuestas-v3-dual-agents"
REGION="us-east-1"

# Función para verificar estado
check_stack_status() {
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null
}

# Función para obtener outputs
get_stack_outputs() {
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table 2>/dev/null
}

# Función para obtener URL del API
get_api_url() {
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text 2>/dev/null
}

# Verificar estado actual
STATUS=$(check_stack_status)

echo "📊 Estado actual: $STATUS"

case $STATUS in
    "CREATE_COMPLETE"|"UPDATE_COMPLETE")
        echo "✅ ¡Despliegue completado exitosamente!"
        echo ""
        echo "📋 Outputs del Stack:"
        get_stack_outputs
        echo ""
        API_URL=$(get_api_url)
        echo "🌐 URL del API Gateway: $API_URL"
        echo ""
        echo "🔧 Próximos pasos:"
        echo "1. Actualizar .env.local con: NEXT_PUBLIC_API_URL=$API_URL"
        echo "2. Probar endpoints:"
        echo "   - GET $API_URL/models"
        echo "   - POST $API_URL/chat"
        echo "3. Hacer build y deploy del frontend"
        ;;
    "CREATE_IN_PROGRESS"|"UPDATE_IN_PROGRESS"|"REVIEW_IN_PROGRESS")
        echo "⏳ Despliegue en progreso... Esperando..."
        echo "💡 Ejecuta este script nuevamente en unos minutos"
        ;;
    "CREATE_FAILED"|"UPDATE_FAILED"|"ROLLBACK_COMPLETE")
        echo "❌ Error en el despliegue"
        echo "🔍 Revisa los eventos del stack:"
        echo "aws cloudformation describe-stack-events --stack-name $STACK_NAME --region $REGION"
        ;;
    "")
        echo "❓ Stack no encontrado o error de acceso"
        echo "🔍 Verifica que el stack existe:"
        echo "aws cloudformation list-stacks --region $REGION --query 'StackSummaries[?StackName==\`$STACK_NAME\`]'"
        ;;
    *)
        echo "⚠️  Estado desconocido: $STATUS"
        ;;
esac

echo ""
echo "🤖 Información de Agentes Bedrock:"
echo "Nova Pro Agent ID: WUGHP2HGH9 (Alias: ZNZ3SYTP5L)"
echo "Claude Agent ID: W3YRJXXIRE (Alias: ULPAGJS0VW)"
