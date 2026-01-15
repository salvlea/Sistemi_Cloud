#!/bin/bash

# Smart ATS Deployment Script
# This script handles the complete deployment of the Smart ATS infrastructure

set -e  # Exit on error

echo "========================================="
echo "Smart ATS Deployment Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
AWS_REGION=${2:-us-east-1}
STACK_NAME="smart-ats-stack-${ENVIRONMENT}"

echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Region: ${AWS_REGION}${NC}"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v sam &> /dev/null; then
    echo -e "${RED}SAM CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Step 1: Build SAM application
echo "========================================="
echo "Step 1: Building SAM application..."
echo "========================================="

cd infrastructure
sam build --use-container --parallel

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Step 2: Deploy infrastructure
echo "========================================="
echo "Step 2: Deploying infrastructure..."
echo "========================================="

sam deploy \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --parameter-overrides Environment=${ENVIRONMENT} \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment successful${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi
echo ""

# Step 3: Get stack outputs
echo "========================================="
echo "Step 3: Retrieving stack outputs..."
echo "========================================="

S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
    --output text \
    --region ${AWS_REGION})

API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text \
    --region ${AWS_REGION})

USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text \
    --region ${AWS_REGION})

CLIENT_ID=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
    --output text \
    --region ${AWS_REGION})

echo -e "${GREEN}Stack Outputs:${NC}"
echo "  S3 Bucket: ${S3_BUCKET}"
echo "  API Endpoint: ${API_ENDPOINT}"
echo "  User Pool ID: ${USER_POOL_ID}"
echo "  Client ID: ${CLIENT_ID}"
echo ""

# Save outputs to .env file for frontend
cd ../frontend
cat > .env <<EOF
AWS_REGION=${AWS_REGION}
S3_BUCKET_NAME=${S3_BUCKET}
API_GATEWAY_URL=${API_ENDPOINT}
COGNITO_USER_POOL_ID=${USER_POOL_ID}
COGNITO_CLIENT_ID=${CLIENT_ID}
DYNAMODB_TABLE=smart-ats-candidates-${ENVIRONMENT}
SECRET_KEY=$(openssl rand -hex 32)
EOF

echo -e "${GREEN}✓ Environment variables saved to frontend/.env${NC}"
echo ""

# Step 4: Build and push Docker image (optional)
echo "========================================="
echo "Step 4: Docker image setup (optional)"
echo "========================================="

read -p "Do you want to build and push Docker image to ECR? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Create ECR repository if it doesn't exist
    ECR_REPO="smart-ats-frontend"
    aws ecr describe-repositories --repository-names ${ECR_REPO} --region ${AWS_REGION} 2>/dev/null || \
        aws ecr create-repository --repository-name ${ECR_REPO} --region ${AWS_REGION}
    
    # Get ECR login
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com
    
    # Build and push
    docker build -t ${ECR_REPO}:latest .
    docker tag ${ECR_REPO}:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest
    docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest
    
    echo -e "${GREEN}✓ Docker image pushed to ECR${NC}"
fi

cd ..

echo ""
echo "========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Set temporary password for Cognito user:"
echo "   aws cognito-idp admin-set-user-password --user-pool-id ${USER_POOL_ID} --username admin@smartats.com --password YourPassword123! --permanent --region ${AWS_REGION}"
echo ""
echo "2. Test API health endpoint:"
echo "   curl ${API_ENDPOINT}/health"
echo ""
echo "3. Run Flask app locally:"
echo "   cd frontend && python app.py"
echo ""
