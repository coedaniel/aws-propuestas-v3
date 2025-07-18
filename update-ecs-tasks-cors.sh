#!/bin/bash

# Script para actualizar Task Definitions de ECS con imágenes que tienen CORS
set -e

# Variables
REGION="us-east-1"
ACCOUNT_ID="035385358261"
ECR_BASE="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# Función para actualizar Task Definition
update_task_definition() {
    local task_family=$1
    local ecr_repo=$2
    local service_name=$3
    
    echo "🔄 Actualizando Task Definition: $task_family"
    
    # Obtener la Task Definition actual
    TASK_DEF=$(aws ecs describe-task-definition --task-definition $task_family --region $REGION --query 'taskDefinition')
    
    # Crear nueva Task Definition con imagen actualizada
    NEW_TASK_DEF=$(echo $TASK_DEF | jq --arg IMAGE "$ECR_BASE/$ecr_repo:cors-enabled" '
        .containerDefinitions[0].image = $IMAGE |
        del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .placementConstraints, .compatibilities, .registeredAt, .registeredBy)
    ')
    
    # Registrar nueva Task Definition
    echo "📝 Registrando nueva Task Definition para $task_family..."
    NEW_TASK_ARN=$(echo $NEW_TASK_DEF | aws ecs register-task-definition --region $REGION --cli-input-json file:///dev/stdin --query 'taskDefinition.taskDefinitionArn' --output text)
    
    echo "✅ Nueva Task Definition registrada: $NEW_TASK_ARN"
    
    # Actualizar servicio ECS si existe
    if [ ! -z "$service_name" ]; then
        echo "🔄 Actualizando servicio ECS: $service_name"
        aws ecs update-service --cluster aws-propuestas-v3-mcp-servers-prod --service $service_name --task-definition $NEW_TASK_ARN --region $REGION --query 'service.serviceName' --output text
        echo "✅ Servicio $service_name actualizado"
    fi
}

echo "🚀 Iniciando actualización de Task Definitions con CORS..."

# Actualizar cada servicio MCP
update_task_definition "aws-propuestas-v3-core-mcp-prod" "aws-propuestas-v3-core-mcp" "aws-propuestas-v3-core-mcp-prod"
update_task_definition "aws-propuestas-v3-diagram-mcp-prod" "aws-propuestas-v3-diagram-mcp" "aws-propuestas-v3-diagram-mcp-prod"
update_task_definition "aws-propuestas-v3-cfn-mcp-prod" "aws-propuestas-v3-cfn-mcp" "aws-propuestas-v3-cfn-mcp-prod"
update_task_definition "aws-propuestas-v3-pricing-mcp-prod" "aws-propuestas-v3-pricing-mcp" "aws-propuestas-v3-pricing-mcp-prod"
update_task_definition "aws-propuestas-v3-awsdocs-mcp-prod" "aws-propuestas-v3-docgen-mcp" "aws-propuestas-v3-awsdocs-mcp-prod"
update_task_definition "aws-propuestas-v3-customdoc-mcp-prod" "aws-propuestas-v3-customdoc-mcp" "aws-propuestas-v3-customdoc-mcp-prod"

echo "🎉 ¡Todas las Task Definitions y servicios ECS han sido actualizados con CORS!"
echo "⏳ Los servicios se están reiniciando con las nuevas imágenes..."
echo "🔍 Verifica el estado en: https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/aws-propuestas-v3-mcp-servers-prod/services"
