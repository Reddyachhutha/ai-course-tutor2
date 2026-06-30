# 🚀 Quick Start - Deployment Ready

## What's Been Added for Production

✅ **Docker Configuration**
- Dockerfiles for backend & frontend
- docker-compose.yml with health checks & volumes
- .dockerignore for optimized builds

✅ **CI/CD Pipeline**
- GitHub Actions workflow (.github/workflows/ci-cd.yml)
- Automated testing, linting, security scanning
- Automated deployment to AWS/GCloud

✅ **Security Hardening**
- CORS, HTTPS, security headers
- Rate limiting middleware
- Environment-based configuration
- Secrets management guide (SECURITY.md)

✅ **Deployment Scripts**
- Local dev setup: scripts/start-dev.sh (Linux/Mac) or start-dev.bat (Windows)
- AWS deployment: scripts/deploy-aws.sh
- Google Cloud deployment: scripts/deploy-gcloud.sh
- Convenient make targets: Makefile

✅ **Documentation**
- DEPLOYMENT.md - Complete deployment guide
- SECURITY.md - Secrets & security best practices
- PRODUCTION_READINESS.md - Pre-deployment checklist
- .env.example - Configuration template

---

## 30-Second Deployment

### Local Docker (Easiest - Try This First!)

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 2. Start services
docker-compose up

# 3. Access
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Windows Users

```bash
# 1. Create .env
copy .env.example .env
# Edit .env in Notepad

# 2. Start Docker Desktop
# 3. Run in PowerShell
docker-compose up

# 4. Open browser to http://localhost:8501
```

---

## Deploy to Cloud

### Option 1: AWS (ECS Fargate)

```bash
# 1. Configure AWS CLI
aws configure

# 2. Deploy
./scripts/deploy-aws.sh
# or on Windows: Scripts\deploy-aws.sh

# 3. Get URL
aws ecs describe-services --cluster ai-tutor --services ai-tutor-service
```

### Option 2: Google Cloud Run

```bash
# 1. Install Google Cloud SDK
gcloud init

# 2. Deploy
./scripts/deploy-gcloud.sh
# or on Windows: powershell -File Scripts\deploy-gcloud.sh

# 3. Check status
gcloud run services describe ai-tutor-backend --platform managed
```

### Option 3: Azure Container Instances

See DEPLOYMENT.md for detailed steps

---

## Next Steps

### Before Production Deployment

1. **Security Setup**
   ```bash
   # Read security guide
   cat SECURITY.md
   
   # Store secrets in cloud vault, NOT .env
   # AWS: AWS Secrets Manager
   # GCP: Cloud Secret Manager
   # Azure: Key Vault
   ```

2. **Testing**
   ```bash
   make test          # Run tests
   make lint          # Check code quality
   make security      # Security scan
   ```

3. **Configuration**
   ```bash
   # Edit .env for production
   ENVIRONMENT=production
   DEBUG=false
   ENFORCE_HTTPS=true
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

4. **Database & Storage**
   - Configure persistent ChromaDB (S3, GCS, Azure Blob)
   - Set up database backups
   - Enable encryption

5. **Monitoring**
   - Set up error tracking (Sentry)
   - Configure logs (CloudWatch, Cloud Logging, etc.)
   - Set up alerts

### Deployment Checklist

Before going live, complete: `PRODUCTION_READINESS.md`

---

## Common Commands

```bash
# Development
make dev              # Start dev environment
make test             # Run tests
make lint             # Check code style

# Docker
make docker           # Start Docker Compose
make docker-build     # Build images
docker-compose logs   # View logs

# Deployment
make deploy-local     # Deploy locally
make deploy-aws       # Deploy to AWS
make deploy-gcloud    # Deploy to GCloud

# Maintenance
make clean            # Clean artifacts
make prod             # Run all production checks
```

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8000/8501
lsof -i :8000
# Kill process
kill -9 <PID>
```

### API Key Error
```bash
# Check .env
cat .env | grep GOOGLE_API_KEY

# Get new key at:
# https://aistudio.google.com/app/apikey
```

### Docker Build Fails
```bash
docker-compose build --no-cache
```

### Can't Connect Backend to Frontend
```bash
# Check backend is running
curl http://localhost:8000/health

# Update .env
BACKEND_URL=http://localhost:8000
```

See DEPLOYMENT.md for more troubleshooting

---

## Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile.backend` | Backend container image |
| `Dockerfile.frontend` | Frontend container image |
| `docker-compose.yml` | Multi-container orchestration |
| `.env.example` | Environment template |
| `DEPLOYMENT.md` | Full deployment guide |
| `SECURITY.md` | Security & secrets guide |
| `PRODUCTION_READINESS.md` | Pre-deployment checklist |
| `Makefile` | Convenient commands |
| `scripts/start-dev.sh` | Dev setup (Linux/Mac) |
| `scripts/start-dev.bat` | Dev setup (Windows) |
| `scripts/deploy-aws.sh` | AWS deployment |
| `scripts/deploy-gcloud.sh` | Google Cloud deployment |
| `.github/workflows/ci-cd.yml` | GitHub Actions pipeline |
| `aws-ecs-task-definition.json` | AWS ECS config |
| `backend/config_prod.py` | Production config |

---

## Support

- **Deployment Issues**: See DEPLOYMENT.md
- **Security Questions**: See SECURITY.md
- **Pre-deployment**: Use PRODUCTION_READINESS.md checklist
- **General Help**: Check troubleshooting section above

---

## You're Ready! 🎉

Your AI Tutor Platform is now production-ready. Choose your deployment method above and get started!

**First Time?** → Start with `docker-compose up`

**Ready for Cloud?** → Choose AWS, GCloud, or Azure deployment

**Full Details?** → Read DEPLOYMENT.md
