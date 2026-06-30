# 🚀 AI Tutor Platform - Deployment Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Security Checklist](#security-checklist)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- Git
- Google Gemini API Key

### 1. Clone & Configure

```bash
# Clone repository
git clone https://github.com/your-org/ai-tutor.git
cd ai-tutor

# Create .env file
cp .env.example .env

# Edit .env with your API keys
# Replace: GOOGLE_API_KEY=your_key_here
nano .env
```

### 2. Install Dependencies

```bash
# Using pip
pip install -e .

# Or using uv (faster)
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

uv pip install -e .
```

### 3. Run Services

**Option A: Separate terminals**

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
streamlit run frontend/app.py
```

**Option B: Docker Compose (Recommended)**

```bash
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Build Docker Images

```bash
# Build both images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Run with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes (data cleanup)
docker-compose down -v
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:8501

# View all services status
docker-compose ps
```

---

## Cloud Deployment

### Option 1: AWS ECS (Elastic Container Service)

#### Prerequisites
- AWS Account
- AWS CLI configured
- ECR (Elastic Container Registry) repository

#### Steps

```bash
# 1. Push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker build -f Dockerfile.backend -t ai-tutor-backend:latest .
docker tag ai-tutor-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-tutor-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-tutor-backend:latest

# Repeat for frontend

# 2. Create ECS task definition (see: aws-ecs-task-definition.json)

# 3. Create ECS service
aws ecs create-service \
  --cluster ai-tutor-cluster \
  --service-name ai-tutor-backend \
  --task-definition ai-tutor-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

### Option 2: Google Cloud Run

#### Prerequisites
- Google Cloud Account
- Cloud SDK installed

#### Steps

```bash
# 1. Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-tutor-backend

# 3. Deploy to Cloud Run
gcloud run deploy ai-tutor-backend \
  --image gcr.io/YOUR_PROJECT_ID/ai-tutor-backend \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars ENVIRONMENT=production \
  --allow-unauthenticated

# Get service URL
gcloud run services describe ai-tutor-backend --platform managed --region us-central1 --format 'value(status.url)'
```

### Option 3: Azure Container Instances

```bash
# 1. Push to ACR (Azure Container Registry)
az acr build --registry YOUR_REGISTRY_NAME \
  --image ai-tutor-backend:latest \
  --file Dockerfile.backend .

# 2. Deploy container instance
az container create \
  --resource-group YOUR_RESOURCE_GROUP \
  --name ai-tutor-backend \
  --image YOUR_REGISTRY_NAME.azurecr.io/ai-tutor-backend:latest \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production \
  --registry-login-server YOUR_REGISTRY_NAME.azurecr.io \
  --registry-username USERNAME \
  --registry-password PASSWORD
```

---

## Security Checklist

### Before Deployment

- [ ] **Environment Variables**
  ```bash
  # Verify no secrets in .env are committed
  git check-ignore .env
  ```

- [ ] **API Keys & Secrets**
  - [ ] Set `GOOGLE_API_KEY` securely (use cloud secrets manager)
  - [ ] Generate strong `SECRET_KEY` for production
  - [ ] Rotate keys regularly

- [ ] **CORS Configuration**
  ```python
  # Update CORS_ORIGINS in .env for your domain
  CORS_ORIGINS=["https://yourdomain.com"]
  ```

- [ ] **SSL/HTTPS**
  - [ ] Obtain SSL certificate (Let's Encrypt, AWS ACM, etc.)
  - [ ] Set `ENFORCE_HTTPS=true` in production

- [ ] **Dependency Scanning**
  ```bash
  # Check for vulnerable packages
  pip-audit
  safety check
  ```

- [ ] **Code Security**
  ```bash
  # Run security scan
  bandit -r backend/
  ```

### Runtime Security

- [ ] Enable rate limiting
- [ ] Set up request logging & monitoring
- [ ] Implement authentication if needed
- [ ] Use secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Enable database encryption
- [ ] Set up firewall rules

---

## Monitoring & Logging

### Logs Configuration

```python
# Configure in config_prod.py
LOG_LEVEL=INFO  # development, staging: DEBUG
SENTRY_DSN=https://your-sentry-key@sentry.io/project-id
```

### Available Endpoints for Health Monitoring

```bash
# Health check
GET /health

# System statistics
GET /stats

# API documentation
GET /docs
GET /redoc
```

### Setting Up Monitoring

**Option 1: Sentry (Error Tracking)**
```bash
pip install sentry-sdk
# Set SENTRY_DSN in .env
```

**Option 2: DataDog**
```bash
pip install datadog
# Configure in your FastAPI app
```

**Option 3: Cloud Native (AWS CloudWatch, Google Cloud Logging)**
```bash
# Docker logs to CloudWatch
docker-compose logs --follow > /dev/null
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Verify API key
echo $GOOGLE_API_KEY

# Check port availability
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Frontend Can't Connect to Backend

```bash
# Update .env
BACKEND_URL=http://backend:8000  # Docker
BACKEND_URL=http://localhost:8000  # Local

# Verify backend is running
curl http://localhost:8000/health
```

### Vector Database Issues

```bash
# Reset ChromaDB
docker-compose exec backend rm -rf /app/chroma_data

# Reinitialize
docker-compose restart backend
```

### Out of Memory

```yaml
# Increase limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
```

---

## Production Deployment Checklist

- [ ] Environment: Set to `production`
- [ ] Debug: Set to `false`
- [ ] SSL/HTTPS: Enabled
- [ ] Secrets: Using secrets manager
- [ ] Logging: Configured with Sentry/DataDog
- [ ] Database: Persistent storage configured
- [ ] Backups: Scheduled
- [ ] Monitoring: Set up alerts
- [ ] Documentation: Updated for team
- [ ] Testing: All tests passing
- [ ] Load testing: Performed

---

## Support & Escalation

For issues or questions:
1. Check logs: `docker-compose logs`
2. Run health check: `/health` endpoint
3. Review troubleshooting section above
4. Contact DevOps team or create issue on GitHub
