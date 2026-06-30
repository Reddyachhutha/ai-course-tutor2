#!/bin/bash
# Deploy script for Google Cloud Run
# Usage: ./scripts/deploy-gcloud.sh

set -e

echo "🚀 Deploying to Google Cloud Run..."

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-your-project-id}
REGION=${GCP_REGION:-us-central1}
IMAGE_TAG=$(git rev-parse --short HEAD)

echo "🔐 Setting up GCP authentication..."
gcloud config set project $PROJECT_ID

echo "📦 Building backend image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/ai-tutor-backend:$IMAGE_TAG \
  --timeout 3600 \
  --file Dockerfile.backend .

echo "🚀 Deploying backend to Cloud Run..."
gcloud run deploy ai-tutor-backend \
  --image gcr.io/$PROJECT_ID/ai-tutor-backend:$IMAGE_TAG \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --cpu 1 \
  --timeout 3600 \
  --set-env-vars ENVIRONMENT=production \
  --allow-unauthenticated

echo "📦 Building frontend image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/ai-tutor-frontend:$IMAGE_TAG \
  --timeout 3600 \
  --file Dockerfile.frontend .

BACKEND_URL=$(gcloud run services describe ai-tutor-backend \
  --platform managed --region $REGION --format 'value(status.url)')

echo "🚀 Deploying frontend to Cloud Run..."
gcloud run deploy ai-tutor-frontend \
  --image gcr.io/$PROJECT_ID/ai-tutor-frontend:$IMAGE_TAG \
  --platform managed \
  --region $REGION \
  --memory 1Gi \
  --timeout 3600 \
  --set-env-vars BACKEND_URL=$BACKEND_URL \
  --allow-unauthenticated

echo "✅ Deployment complete!"
echo ""
echo "📍 Backend URL: $BACKEND_URL"
echo "📍 Frontend URL: $(gcloud run services describe ai-tutor-frontend --platform managed --region $REGION --format 'value(status.url)')"
