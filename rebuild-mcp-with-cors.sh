#!/bin/bash

# Script para reconstruir y subir imágenes MCP con CORS habilitado
set -e

# Variables
REGION="us-east-1"
ACCOUNT_ID="035385358261"
ECR_BASE="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# Autenticar con ECR
echo "🔐 Autenticando con ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_BASE

# Función para construir y subir imagen
build_and_push() {
    local service_name=$1
    local dockerfile_path=$2
    local ecr_repo=$3
    
    echo "🔨 Construyendo imagen para $service_name..."
    
    # Construir imagen
    docker build -t $service_name:cors-enabled $dockerfile_path
    
    # Etiquetar para ECR
    docker tag $service_name:cors-enabled $ECR_BASE/$ecr_repo:latest
    docker tag $service_name:cors-enabled $ECR_BASE/$ecr_repo:cors-enabled
    
    # Subir a ECR
    echo "📤 Subiendo $service_name a ECR..."
    docker push $ECR_BASE/$ecr_repo:latest
    docker push $ECR_BASE/$ecr_repo:cors-enabled
    
    echo "✅ $service_name completado"
}

# Construir y subir cada servicio MCP
echo "🚀 Iniciando construcción de imágenes MCP con CORS..."

# Core MCP
build_and_push "core-mcp" "official-mcp-servers/core-mcp" "aws-propuestas-v3-core-mcp"

# Diagram MCP
build_and_push "diagram-mcp" "official-mcp-servers/diagram-mcp" "aws-propuestas-v3-diagram-mcp"

# CloudFormation MCP
build_and_push "cfn-mcp" "official-mcp-servers/cfn-mcp" "aws-propuestas-v3-cfn-mcp"

# Pricing MCP
build_and_push "pricing-mcp" "official-mcp-servers/pricing-mcp" "aws-propuestas-v3-pricing-mcp"

# DocGen MCP
build_and_push "docgen-mcp" "official-mcp-servers/docgen-mcp" "aws-propuestas-v3-docgen-mcp"

# CustomDoc MCP
build_and_push "customdoc-mcp" "official-mcp-servers/document-generator" "aws-propuestas-v3-customdoc-mcp"

echo "🎉 ¡Todas las imágenes MCP han sido reconstruidas y subidas con CORS habilitado!"
echo "📋 Próximo paso: Actualizar las Task Definitions de ECS para usar las nuevas imágenes"
