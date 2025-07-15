#!/bin/bash

# Deploy MCP Servers to ECS - AWS Propuestas V3
# This script builds and deploys the MCP servers as Docker containers to ECS

set -e

# Configuration
PROJECT_NAME="aws-propuestas-v3"
ENVIRONMENT="${ENVIRONMENT:-prod}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Deploying MCP Servers for AWS Propuestas V3"
echo "Project: $PROJECT_NAME"
echo "Environment: $ENVIRONMENT"
echo "Region: $AWS_REGION"
echo "Account: $AWS_ACCOUNT_ID"
echo ""

# Function to create ECR repository if it doesn't exist
create_ecr_repo() {
    local repo_name=$1
    echo "📦 Checking ECR repository: $repo_name"
    
    if ! aws ecr describe-repositories --repository-names "$repo_name" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "Creating ECR repository: $repo_name"
        aws ecr create-repository \
            --repository-name "$repo_name" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true
    else
        echo "ECR repository $repo_name already exists"
    fi
}

# Function to build and push Docker image
build_and_push() {
    local service_name=$1
    local service_path=$2
    local repo_name="${PROJECT_NAME}-${service_name}"
    
    echo ""
    echo "🔨 Building and pushing $service_name"
    echo "Service path: $service_path"
    echo "Repository: $repo_name"
    
    # Create ECR repository
    create_ecr_repo "$repo_name"
    
    # Get ECR login token
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Build Docker image
    cd "$service_path"
    docker build -t "$repo_name:latest" .
    
    # Tag for ECR
    docker tag "$repo_name:latest" "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${repo_name}:latest"
    
    # Push to ECR
    docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${repo_name}:latest"
    
    echo "✅ Successfully pushed $service_name to ECR"
    cd - > /dev/null
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Build and push each MCP server
echo "🏗️  Building MCP Server Docker images..."

build_and_push "document-generator" "mcp-servers/document-generator"
build_and_push "cloudformation-generator" "mcp-servers/cloudformation-generator"
build_and_push "cost-analysis" "mcp-servers/cost-analysis"

echo ""
echo "🚀 Deploying ECS infrastructure..."

# Deploy ECS infrastructure
aws cloudformation deploy \
    --template-file infrastructure/ecs-mcp-servers.yaml \
    --stack-name "${PROJECT_NAME}-mcp-servers-${ENVIRONMENT}" \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
        ProjectName="$PROJECT_NAME" \
    --capabilities CAPABILITY_IAM \
    --region "$AWS_REGION"

echo ""
echo "📊 Getting deployment information..."

# Get ALB DNS name
ALB_DNS=$(aws cloudformation describe-stacks \
    --stack-name "${PROJECT_NAME}-mcp-servers-${ENVIRONMENT}" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text)

echo ""
echo "✅ MCP Servers deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "├── ECS Cluster: ${PROJECT_NAME}-mcp-cluster-${ENVIRONMENT}"
echo "├── Load Balancer: $ALB_DNS"
echo "├── Document Generator: http://$ALB_DNS/document-generator"
echo "├── CloudFormation Generator: http://$ALB_DNS/cloudformation-generator"
echo "└── Cost Analysis: http://$ALB_DNS/cost-analysis"
echo ""

# Test endpoints
echo "🧪 Testing MCP server endpoints..."

test_endpoint() {
    local name=$1
    local url=$2
    
    echo -n "Testing $name... "
    if curl -s --max-time 10 "$url/health" >/dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "⚠️  Not ready yet (this is normal, services may still be starting)"
    fi
}

# Wait a bit for services to start
echo "Waiting 30 seconds for services to start..."
sleep 30

test_endpoint "Document Generator" "http://$ALB_DNS/document-generator"
test_endpoint "CloudFormation Generator" "http://$ALB_DNS/cloudformation-generator"
test_endpoint "Cost Analysis" "http://$ALB_DNS/cost-analysis"

echo ""
echo "🔧 Next Steps:"
echo "1. Update your Lambda functions to use these MCP server endpoints"
echo "2. Configure your frontend to call the main Lambda function"
echo "3. Test the complete workflow"
echo ""
echo "📝 Environment Variables for Lambda:"
echo "DOCUMENT_GENERATOR_ENDPOINT=http://$ALB_DNS/document-generator"
echo "CLOUDFORMATION_GENERATOR_ENDPOINT=http://$ALB_DNS/cloudformation-generator"
echo "COST_ANALYSIS_ENDPOINT=http://$ALB_DNS/cost-analysis"
echo ""

# Save endpoints to file for later use
cat > mcp-endpoints.env << EOF
# MCP Server Endpoints - Generated $(date)
DOCUMENT_GENERATOR_ENDPOINT=http://$ALB_DNS/document-generator
CLOUDFORMATION_GENERATOR_ENDPOINT=http://$ALB_DNS/cloudformation-generator
COST_ANALYSIS_ENDPOINT=http://$ALB_DNS/cost-analysis
ALB_DNS=$ALB_DNS
EOF

echo "💾 Endpoints saved to mcp-endpoints.env"
echo ""
echo "🎉 MCP Servers are now running on ECS!"
echo "You can monitor them in the AWS Console:"
echo "https://console.aws.amazon.com/ecs/home?region=${AWS_REGION}#/clusters/${PROJECT_NAME}-mcp-cluster-${ENVIRONMENT}/services"
