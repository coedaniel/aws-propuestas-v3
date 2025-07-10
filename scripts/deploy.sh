#!/bin/bash

# =============================================================================
# AWS PROPUESTAS V3 - DEPLOYMENT SCRIPT
# =============================================================================

set -e

echo "🚀 Deploying AWS Propuestas v3..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-prod}
REGION=${REGION:-us-east-1}
PROJECT_NAME="aws-propuestas-v3"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}"

echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Region: ${REGION}${NC}"
echo -e "${BLUE}Stack Name: ${STACK_NAME}${NC}"

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI.${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install Node.js and npm.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure'.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Build frontend
echo -e "\n${YELLOW}📦 Building frontend...${NC}"
npm install
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

# Deploy to Amplify (if configured)
if [ ! -z "$AMPLIFY_APP_ID" ]; then
    echo -e "\n${YELLOW}🚀 Deploying to AWS Amplify...${NC}"
    
    # Create deployment
    aws amplify start-job \
        --app-id $AMPLIFY_APP_ID \
        --branch-name main \
        --job-type RELEASE \
        --region $REGION
    
    echo -e "${GREEN}✅ Amplify deployment started${NC}"
    echo -e "${BLUE}Check status at: https://console.aws.amazon.com/amplify/home?region=${REGION}#/${AMPLIFY_APP_ID}${NC}"
else
    echo -e "${YELLOW}⚠️  AMPLIFY_APP_ID not set. Skipping Amplify deployment.${NC}"
    echo -e "${BLUE}To deploy to Amplify:${NC}"
    echo -e "${BLUE}1. Create Amplify app in AWS Console${NC}"
    echo -e "${BLUE}2. Connect your GitHub repository${NC}"
    echo -e "${BLUE}3. Set AMPLIFY_APP_ID environment variable${NC}"
fi

# Success message
echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "\n${BLUE}📋 Next steps:${NC}"
echo -e "${BLUE}1. Configure environment variables in Amplify Console${NC}"
echo -e "${BLUE}2. Set up DynamoDB tables if needed${NC}"
echo -e "${BLUE}3. Configure S3 bucket for documents${NC}"
echo -e "${BLUE}4. Test the application${NC}"

echo -e "\n${BLUE}🔗 Useful links:${NC}"
echo -e "${BLUE}• AWS Amplify Console: https://console.aws.amazon.com/amplify/home?region=${REGION}${NC}"
echo -e "${BLUE}• DynamoDB Console: https://console.aws.amazon.com/dynamodb/home?region=${REGION}${NC}"
echo -e "${BLUE}• S3 Console: https://console.aws.amazon.com/s3/home?region=${REGION}${NC}"
echo -e "${BLUE}• Bedrock Console: https://console.aws.amazon.com/bedrock/home?region=${REGION}${NC}"
