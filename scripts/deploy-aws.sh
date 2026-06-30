#!/bin/bash
# Deploy script for AWS
# Usage: ./scripts/deploy-aws.sh

set -e

echo "🚀 Deploying to AWS..."

# Configuration
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
IMAGE_TAG=$(git rev-parse --short HEAD)

echo "📦 Building Docker images..."
docker build -f Dockerfile.backend -t ai-tutor-backend:$IMAGE_TAG .
docker build -f Dockerfile.frontend -t ai-tutor-frontend:$IMAGE_TAG .

echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO

echo "📤 Pushing to ECR..."
docker tag ai-tutor-backend:$IMAGE_TAG $ECR_REPO/ai-tutor-backend:$IMAGE_TAG
docker tag ai-tutor-backend:$IMAGE_TAG $ECR_REPO/ai-tutor-backend:latest
docker push $ECR_REPO/ai-tutor-backend:$IMAGE_TAG
docker push $ECR_REPO/ai-tutor-backend:latest

docker tag ai-tutor-frontend:$IMAGE_TAG $ECR_REPO/ai-tutor-frontend:$IMAGE_TAG
docker tag ai-tutor-frontend:$IMAGE_TAG $ECR_REPO/ai-tutor-frontend:latest
docker push $ECR_REPO/ai-tutor-frontend:$IMAGE_TAG
docker push $ECR_REPO/ai-tutor-frontend:latest

echo "📋 Registering ECS task definition..."
# Update the task definition with new image tags
sed -i "s|YOUR_ACCOUNT_ID|$ACCOUNT_ID|g" aws-ecs-task-definition.json

aws ecs register-task-definition \
  --cli-input-json file://aws-ecs-task-definition.json

echo "🔄 Updating ECS service..."
aws ecs update-service \
  --cluster ai-tutor-cluster \
  --service ai-tutor-service \
  --force-new-deployment \
  --region $REGION

echo "✅ Deployment started!"
echo "📊 Monitor progress in AWS Console"
