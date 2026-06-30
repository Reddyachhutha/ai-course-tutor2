# 🔐 Security & Secrets Management Guide

## Overview
This guide covers best practices for managing secrets and securing the AI Tutor Platform for production deployment.

---

## Environment Variables & Secrets

### Critical Secrets
Never commit these to version control:
- `GOOGLE_API_KEY` - Google Gemini API key
- `SECRET_KEY` - FastAPI session/encryption key
- AWS/GCP credentials
- Database passwords
- API tokens

### Using .env Files

```bash
# Development
cp .env.example .env
# Edit with your development keys

# Production - Use secrets manager instead
```

### ⚠️ Never Do This:
```python
# ❌ WRONG - Hardcoded secrets
GOOGLE_API_KEY = "sk-1234567890abcdef"

# ❌ WRONG - Committed to git
with open(".env") as f:
    config = json.load(f)

# ❌ WRONG - In environment variable during deploy
export GOOGLE_API_KEY="..."  # Will appear in process list
```

### ✅ Correct Approach:
```python
# Use Pydantic settings with validation
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str  # Required, must be set
    
    @field_validator("GOOGLE_API_KEY")
    def validate_key(cls, v):
        if not v:
            raise ValueError("GOOGLE_API_KEY must be set")
        return v
```

---

## Cloud Secrets Management

### AWS Secrets Manager

```bash
# Store secret
aws secretsmanager create-secret \
  --name ai-tutor/google-api-key \
  --secret-string "your-api-key-here"

# Retrieve in application
import boto3
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='ai-tutor/google-api-key')
api_key = response['SecretString']

# In ECS task definition
{
  "secrets": [{
    "name": "GOOGLE_API_KEY",
    "valueFrom": "arn:aws:secretsmanager:region:account:secret:ai-tutor/google-api-key"
  }]
}
```

### Google Cloud Secret Manager

```bash
# Store secret
echo -n "your-api-key-here" | \
  gcloud secrets create ai-tutor-google-api-key \
    --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding ai-tutor-google-api-key \
  --member="serviceAccount:PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# In Cloud Run
gcloud run deploy ai-tutor-backend \
  --update-secrets GOOGLE_API_KEY=ai-tutor-google-api-key:latest
```

### Azure Key Vault

```bash
# Store secret
az keyvault secret set \
  --vault-name "ai-tutor-vault" \
  --name "google-api-key" \
  --value "your-api-key-here"

# In application
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://ai-tutor-vault.vault.azure.net", credential=credential)
secret = client.get_secret("google-api-key")
api_key = secret.value
```

---

## API Key Rotation

### Process
1. Generate new API key in Google Cloud Console
2. Update secret in secrets manager
3. Restart services (without downtime)
4. Delete old key after verification

```bash
# AWS example - update secret
aws secretsmanager update-secret \
  --secret-id ai-tutor/google-api-key \
  --secret-string "new-api-key-here"

# ECS - force new deployment
aws ecs update-service \
  --cluster ai-tutor-cluster \
  --service ai-tutor-service \
  --force-new-deployment
```

---

## Database Security

### Encryption at Rest

**AWS RDS:**
```bash
# Enable encryption
aws rds modify-db-instance \
  --db-instance-identifier ai-tutor-db \
  --storage-encrypted \
  --apply-immediately
```

**Azure:**
```bash
az postgres server update \
  --name ai-tutor-db \
  --resource-group ai-tutor-rg \
  --ssl-enforcement ENABLED
```

### Encryption in Transit

Always use SSL/TLS:
```python
# PostgreSQL connection
DATABASE_URL = "postgresql+psycopg2://user:pass@host/db?sslmode=require"
```

---

## Access Control

### API Authentication (Recommended)

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

@app.post("/api/upload")
async def upload(file: UploadFile, credentials: HTTPAuthCredentials = Depends(security)):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token")
    # Process file
```

### Rate Limiting Per API Key

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("100/minute")
async def chat(request: Request, msg: str):
    # Process chat
```

---

## Network Security

### Firewall Rules

**AWS Security Group:**
```bash
# Allow HTTPS only
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Deny HTTP
aws ec2 revoke-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

### VPC Isolation

```yaml
# docker-compose.yml
networks:
  ai-tutor-private:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  backend:
    networks:
      - ai-tutor-private
```

---

## SSL/TLS Certificates

### Let's Encrypt (Free)

```bash
# Using Certbot
sudo apt-get install certbot

certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Application Level

```python
# Force HTTPS redirect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENFORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

## Dependency Security

### Regular Vulnerability Scanning

```bash
# Check for vulnerable packages
pip-audit
safety check

# Update dependencies
pip install --upgrade pip
pip install --upgrade -e .
```

### GitHub Dependabot

Add to `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Logging & Monitoring

### Sensitive Data

```python
# ❌ DON'T log API keys
logger.info(f"Using API key: {GOOGLE_API_KEY}")

# ✅ DO mask sensitive data
def mask_secret(secret: str, visible_chars: int = 4) -> str:
    if len(secret) <= visible_chars:
        return "*" * len(secret)
    return secret[:visible_chars] + "*" * (len(secret) - visible_chars)

logger.info(f"Using API key: {mask_secret(GOOGLE_API_KEY)}")
```

### Log Rotation

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'app.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
```

---

## Incident Response

### If Secrets Are Compromised

1. **Immediate**: Revoke compromised credentials
   ```bash
   # Google Gemini API
   # Delete key from Google Cloud Console
   # Generate new key
   ```

2. **Update**: Change all secrets
   ```bash
   aws secretsmanager update-secret --secret-id ai-tutor/google-api-key ...
   ```

3. **Deploy**: Force service restart
   ```bash
   docker-compose restart backend
   ```

4. **Audit**: Review logs for unauthorized access
   ```bash
   # Check recent API calls
   gcloud logging read "resource.type=api" --limit 100
   ```

5. **Document**: Update incident log for compliance

---

## Pre-Deployment Checklist

- [ ] No hardcoded secrets in code
- [ ] All secrets in secrets manager
- [ ] API keys rotated (if not first deploy)
- [ ] SSL/TLS certificates valid
- [ ] Firewall rules configured
- [ ] Database encrypted
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Incident response plan documented
- [ ] Team trained on security practices

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [12 Factor App](https://12factor.net/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [Google Cloud Security](https://cloud.google.com/security)
