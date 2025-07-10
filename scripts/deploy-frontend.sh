#!/bin/bash

# =============================================================================
# AWS PROPUESTAS V3 - FRONTEND DEPLOYMENT SCRIPT
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGION=${REGION:-us-east-1}
APP_NAME="aws-propuestas-v3"
GITHUB_REPO="https://github.com/coedaniel/aws-propuestas-v3"

echo -e "${BLUE}🚀 Deploying AWS Propuestas v3 Frontend...${NC}"
echo -e "${BLUE}Region: ${REGION}${NC}"
echo -e "${BLUE}App Name: ${APP_NAME}${NC}"

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

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

# Build frontend
echo -e "\n${YELLOW}📦 Building frontend...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

# Check if Amplify app exists
echo -e "\n${YELLOW}🔍 Checking if Amplify app exists...${NC}"

APP_ID=$(aws amplify list-apps --region ${REGION} --query "apps[?name=='${APP_NAME}'].appId" --output text 2>/dev/null || echo "")

if [ -z "$APP_ID" ]; then
    echo -e "${YELLOW}📱 Creating new Amplify app...${NC}"
    
    # Create Amplify app
    APP_ID=$(aws amplify create-app \
        --name ${APP_NAME} \
        --description "Sistema conversacional profesional para generar propuestas ejecutivas de soluciones AWS con IA" \
        --repository ${GITHUB_REPO} \
        --platform WEB \
        --region ${REGION} \
        --query 'app.appId' \
        --output text)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Amplify app created: ${APP_ID}${NC}"
    else
        echo -e "${RED}❌ Failed to create Amplify app${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Found existing Amplify app: ${APP_ID}${NC}"
fi

# Set environment variables
echo -e "\n${YELLOW}🔧 Setting environment variables...${NC}"

aws amplify put-backend-environment \
    --app-id ${APP_ID} \
    --environment-name main \
    --region ${REGION} \
    --deployment-artifacts ${APP_NAME}-deployment \
    --stack-name ${APP_NAME}-backend 2>/dev/null || true

# Update environment variables
aws amplify update-app \
    --app-id ${APP_ID} \
    --region ${REGION} \
    --environment-variables \
        NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod \
        NEXT_PUBLIC_REGION=us-east-1 \
        NEXT_PUBLIC_ENVIRONMENT=prod \
        AMPLIFY_MONOREPO_APP_ROOT=. \
        AMPLIFY_DIFF_DEPLOY=false \
        _LIVE_UPDATES='[{"name":"Amplify CLI","pkg":"@aws-amplify/cli","type":"npm","version":"latest"}]' \
    > /dev/null

echo -e "${GREEN}✅ Environment variables configured${NC}"

# Create or update branch
echo -e "\n${YELLOW}🌿 Setting up main branch...${NC}"

# Check if branch exists
BRANCH_EXISTS=$(aws amplify list-branches --app-id ${APP_ID} --region ${REGION} --query "branches[?branchName=='main'].branchName" --output text 2>/dev/null || echo "")

if [ -z "$BRANCH_EXISTS" ]; then
    echo -e "${YELLOW}Creating main branch...${NC}"
    
    aws amplify create-branch \
        --app-id ${APP_ID} \
        --branch-name main \
        --region ${REGION} \
        --description "Main production branch" \
        --enable-auto-build \
        --environment-variables \
            NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod \
            NEXT_PUBLIC_REGION=us-east-1 \
            NEXT_PUBLIC_ENVIRONMENT=prod \
        > /dev/null
    
    echo -e "${GREEN}✅ Main branch created${NC}"
else
    echo -e "${GREEN}✅ Main branch already exists${NC}"
fi

# Start deployment
echo -e "\n${YELLOW}🚀 Starting deployment...${NC}"

JOB_ID=$(aws amplify start-job \
    --app-id ${APP_ID} \
    --branch-name main \
    --job-type RELEASE \
    --region ${REGION} \
    --query 'jobSummary.jobId' \
    --output text)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment started: ${JOB_ID}${NC}"
else
    echo -e "${RED}❌ Failed to start deployment${NC}"
    exit 1
fi

# Get app URL
APP_URL="https://main.${APP_ID}.amplifyapp.com"

# Success message
echo -e "\n${GREEN}🎉 Frontend deployment initiated successfully!${NC}"
echo -e "\n${BLUE}📋 Deployment Information:${NC}"
echo -e "${BLUE}==========================${NC}"
echo -e "${BLUE}🌐 App ID: ${APP_ID}${NC}"
echo -e "${BLUE}🔗 App URL: ${APP_URL}${NC}"
echo -e "${BLUE}📊 Job ID: ${JOB_ID}${NC}"
echo -e "${BLUE}🎯 Backend API: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod${NC}"

echo -e "\n${BLUE}🔗 Useful links:${NC}"
echo -e "${BLUE}• Amplify Console: https://console.aws.amazon.com/amplify/home?region=${REGION}#/${APP_ID}${NC}"
echo -e "${BLUE}• App URL: ${APP_URL}${NC}"
echo -e "${BLUE}• GitHub Repo: ${GITHUB_REPO}${NC}"

echo -e "\n${YELLOW}⏳ Deployment is in progress...${NC}"
echo -e "${YELLOW}Check the Amplify Console for real-time status updates.${NC}"
echo -e "${YELLOW}The app will be available at ${APP_URL} once deployment completes.${NC}"

echo -e "\n${GREEN}🎊 AWS Propuestas v3 deployment completed!${NC}"
