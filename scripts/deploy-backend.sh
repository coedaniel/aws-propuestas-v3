#!/bin/bash

# =============================================================================
# AWS PROPUESTAS V3 - BACKEND DEPLOYMENT SCRIPT
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-prod}
REGION=${REGION:-us-east-1}
STACK_NAME="aws-propuestas-v3-${ENVIRONMENT}"

echo -e "${BLUE}🚀 Deploying AWS Propuestas v3 Backend...${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Region: ${REGION}${NC}"
echo -e "${BLUE}Stack Name: ${STACK_NAME}${NC}"

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI not found. Please install SAM CLI.${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure'.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Build SAM application
echo -e "\n${YELLOW}📦 Building SAM application...${NC}"

sam build --template-file infrastructure/template.yaml

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SAM build successful${NC}"
else
    echo -e "${RED}❌ SAM build failed${NC}"
    exit 1
fi

# Deploy to AWS
echo -e "\n${YELLOW}🚀 Deploying to AWS...${NC}"

sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name ${STACK_NAME} \
    --capabilities CAPABILITY_IAM \
    --region ${REGION} \
    --parameter-overrides Environment=${ENVIRONMENT} \
    --resolve-s3 \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend deployed successfully!${NC}"
else
    echo -e "${RED}❌ Backend deployment failed${NC}"
    exit 1
fi

# Get stack outputs
echo -e "\n${YELLOW}📋 Getting deployment information...${NC}"

API_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text)

CHAT_TABLE=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ChatSessionsTableName`].OutputValue' \
    --output text)

PROJECTS_TABLE=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ProjectsTableName`].OutputValue' \
    --output text)

DOCUMENTS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
    --output text)

# Display deployment information
echo -e "\n${GREEN}✅ Backend deployed successfully!${NC}"
echo -e "\n${BLUE}📋 Deployment Information:${NC}"
echo -e "${BLUE}==========================${NC}"
echo -e "${BLUE}🌐 API Gateway URL: ${API_URL}${NC}"
echo -e "${BLUE}📊 Chat Sessions Table: ${CHAT_TABLE}${NC}"
echo -e "${BLUE}📁 Projects Table: ${PROJECTS_TABLE}${NC}"
echo -e "${BLUE}🗂️  Documents Bucket: ${DOCUMENTS_BUCKET}${NC}"

echo -e "\n${BLUE}🔧 Environment Variables for Frontend:${NC}"
echo -e "${BLUE}NEXT_PUBLIC_API_URL=${API_URL}${NC}"
echo -e "${BLUE}NEXT_PUBLIC_REGION=${REGION}${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "${YELLOW}1. Update your frontend environment variables${NC}"
echo -e "${YELLOW}2. Deploy the frontend using: npm run build${NC}"
echo -e "${YELLOW}3. Test the API endpoints${NC}"

echo -e "\n${BLUE}🧪 Test API:${NC}"
echo -e "${BLUE}curl -X GET ${API_URL}/health${NC}"

echo -e "\n${GREEN}🎉 Backend deployment completed!${NC}"
