#!/bin/bash

# Build and Push MCP Server Docker Images to ECR
# This script builds all MCP server images and pushes them to ECR

set -e

# Configuration
PROJECT_NAME="aws-propuestas-v3"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "🚀 Building and pushing MCP Server Docker images..."
echo "Project: ${PROJECT_NAME}"
echo "Region: ${AWS_REGION}"
echo "Account: ${AWS_ACCOUNT_ID}"
echo "Registry: ${ECR_REGISTRY}"

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Function to create ECR repository if it doesn't exist
create_ecr_repo() {
    local repo_name=$1
    echo "📦 Checking ECR repository: ${repo_name}"
    
    if ! aws ecr describe-repositories --repository-names ${repo_name} --region ${AWS_REGION} >/dev/null 2>&1; then
        echo "Creating ECR repository: ${repo_name}"
        aws ecr create-repository --repository-name ${repo_name} --region ${AWS_REGION}
    else
        echo "ECR repository ${repo_name} already exists"
    fi
}

# Function to build and push Docker image
build_and_push() {
    local service_name=$1
    local dockerfile_path=$2
    local image_name="${PROJECT_NAME}-${service_name}"
    local full_image_name="${ECR_REGISTRY}/${image_name}:latest"
    
    echo "🔨 Building ${service_name} image..."
    
    # Create ECR repository
    create_ecr_repo ${image_name}
    
    # Build Docker image
    docker build -t ${image_name}:latest ${dockerfile_path}
    
    # Tag for ECR
    docker tag ${image_name}:latest ${full_image_name}
    
    # Push to ECR
    echo "📤 Pushing ${service_name} image to ECR..."
    docker push ${full_image_name}
    
    echo "✅ Successfully pushed ${full_image_name}"
}

# Build and push all MCP server images
echo "🏗️  Building Official MCP Servers..."

# Core MCP Server
build_and_push "core-mcp" "./official-mcp-servers/core-mcp/"

# Pricing MCP Server
build_and_push "pricing-mcp" "./official-mcp-servers/pricing-mcp/"

# AWS Documentation MCP Server (corrected from docgen to awsdocs)
build_and_push "docgen-mcp" "./official-mcp-servers/docgen-mcp/"

# CloudFormation MCP Server
build_and_push "cfn-mcp" "./official-mcp-servers/cfn-mcp/"

# Diagram MCP Server
build_and_push "diagram-mcp" "./official-mcp-servers/diagram-mcp/"

echo "🏗️  Building Custom MCP Servers..."

# Custom Document Generator MCP Server
build_and_push "customdoc-mcp" "./custom-mcp-servers/document-generator-mcp/"

echo "🎉 All MCP server images built and pushed successfully!"
echo ""
echo "📋 Summary of pushed images:"
echo "- ${ECR_REGISTRY}/${PROJECT_NAME}-core-mcp:latest"
echo "- ${ECR_REGISTRY}/${PROJECT_NAME}-pricing-mcp:latest"
echo "- ${ECR_REGISTRY}/${PROJECT_NAME}-docgen-mcp:latest"
echo "- ${ECR_REGISTRY}/${PROJECT_NAME}-cfn-mcp:latest"
echo "- ${ECR_REGISTRY}/${PROJECT_NAME}-diagram-mcp:latest"
echo "- ${ECR_REGISTRY}/${PROJECT_NAME}-customdoc-mcp:latest"
echo ""
echo "🚀 Ready to deploy ECS services!"
