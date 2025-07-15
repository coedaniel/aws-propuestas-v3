#!/bin/bash

# Script to force update all ECS services with new Docker images
set -e

echo "🔄 Updating all ECS services with new images..."

CLUSTER_NAME="aws-propuestas-v3-official-mcp-prod"
REGION="us-east-1"

# List of services to update
SERVICES=(
    "aws-propuestas-v3-core-mcp-prod"
    "aws-propuestas-v3-pricing-mcp-prod"
    "aws-propuestas-v3-awsdocs-mcp-prod"
    "aws-propuestas-v3-cfn-mcp-prod"
    "aws-propuestas-v3-diagram-mcp-prod"
    "aws-propuestas-v3-customdoc-mcp-prod"
)

for service in "${SERVICES[@]}"; do
    echo "🔄 Updating service: $service"
    
    aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$service" \
        --force-new-deployment \
        --region "$REGION" \
        --output table \
        --query 'service.{ServiceName:serviceName,Status:status,RunningCount:runningCount,PendingCount:pendingCount}' || echo "❌ Failed to update $service"
    
    echo "✅ Update initiated for $service"
    echo ""
done

echo "🎉 All services update initiated!"
echo ""
echo "📋 Monitor deployment progress:"
echo "aws ecs describe-services --cluster $CLUSTER_NAME --services ${SERVICES[*]} --region $REGION"
echo ""
echo "⏱️  Services will take 2-3 minutes to fully deploy new images"
