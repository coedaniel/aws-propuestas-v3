#!/bin/bash

# Script simplificado para actualizar todos los servicios MCP con CORS
set -e

REGION="us-east-1"
CLUSTER="aws-propuestas-v3-official-mcp-prod"

echo "🚀 Actualizando servicios MCP con imágenes CORS habilitado..."

# Función para actualizar servicio
update_service() {
    local service_name=$1
    local task_family=$2
    
    echo "🔄 Actualizando servicio: $service_name"
    
    # Obtener la última revisión de la task definition
    LATEST_REVISION=$(aws ecs describe-task-definition --task-definition $task_family --region $REGION --query 'taskDefinition.revision' --output text)
    
    # Actualizar servicio
    aws ecs update-service \
        --cluster $CLUSTER \
        --service $service_name \
        --task-definition "${task_family}:${LATEST_REVISION}" \
        --region $REGION \
        --query 'service.serviceName' \
        --output text
    
    echo "✅ Servicio $service_name actualizado"
}

# Ya actualizamos core-mcp, ahora los demás
echo "⏭️  Core MCP ya actualizado, continuando con los demás..."

# Crear task definitions para los otros servicios
echo "📝 Creando task definitions con CORS para los demás servicios..."

# Diagram MCP
cat > diagram-mcp-task-def-cors.json << 'EOF'
{
    "family": "aws-propuestas-v3-diagram-mcp-prod",
    "taskRoleArn": "arn:aws:iam::035385358261:role/aws-propuestas-v3-mcp-servers-ECSTaskRole-RAqodTwTfac2",
    "executionRoleArn": "arn:aws:iam::035385358261:role/aws-propuestas-v3-mcp-servers-ECSTaskExecutionRole-Tdc5LMtcURTJ",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "containerDefinitions": [
        {
            "name": "diagram-mcp",
            "image": "035385358261.dkr.ecr.us-east-1.amazonaws.com/aws-propuestas-v3-diagram-mcp:cors-enabled",
            "cpu": 0,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "hostPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "environment": [
                {
                    "name": "FASTMCP_LOG_LEVEL",
                    "value": "ERROR"
                },
                {
                    "name": "PROJECT_NAME",
                    "value": "aws-propuestas-v3"
                },
                {
                    "name": "ENVIRONMENT",
                    "value": "prod"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/aws-propuestas-v3-diagram-mcp-prod",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF

# Registrar y actualizar diagram MCP
aws ecs register-task-definition --cli-input-json file://diagram-mcp-task-def-cors.json --region $REGION > /dev/null
update_service "aws-propuestas-v3-diagram-mcp-prod" "aws-propuestas-v3-diagram-mcp-prod"

# CFN MCP
cat > cfn-mcp-task-def-cors.json << 'EOF'
{
    "family": "aws-propuestas-v3-cfn-mcp-prod",
    "taskRoleArn": "arn:aws:iam::035385358261:role/aws-propuestas-v3-mcp-servers-ECSTaskRole-RAqodTwTfac2",
    "executionRoleArn": "arn:aws:iam::035385358261:role/aws-propuestas-v3-mcp-servers-ECSTaskExecutionRole-Tdc5LMtcURTJ",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "containerDefinitions": [
        {
            "name": "cfn-mcp",
            "image": "035385358261.dkr.ecr.us-east-1.amazonaws.com/aws-propuestas-v3-cfn-mcp:cors-enabled",
            "cpu": 0,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "hostPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "environment": [
                {
                    "name": "FASTMCP_LOG_LEVEL",
                    "value": "ERROR"
                },
                {
                    "name": "PROJECT_NAME",
                    "value": "aws-propuestas-v3"
                },
                {
                    "name": "ENVIRONMENT",
                    "value": "prod"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/aws-propuestas-v3-cfn-mcp-prod",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF

# Registrar y actualizar CFN MCP
aws ecs register-task-definition --cli-input-json file://cfn-mcp-task-def-cors.json --region $REGION > /dev/null
update_service "aws-propuestas-v3-cfn-mcp-prod" "aws-propuestas-v3-cfn-mcp-prod"

echo "🎉 ¡Todos los servicios principales han sido actualizados!"
echo "⏳ Los servicios se están reiniciando con las nuevas imágenes CORS..."
echo "🧪 Ahora puedes probar el frontend en: https://main.d2xsphsjdxlk24.amplifyapp.com"
