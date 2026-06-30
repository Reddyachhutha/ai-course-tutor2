# 🚀 Render Deployment Guide for AI Tutor Platform

## Quick Start

Deploy your AI Tutor Platform to Render in 5 minutes with Docker containers.

---

## Prerequisites

- GitHub account with your repo: `https://github.com/Reddyachhutha/ai-course-tutor2.git`
- Render account (free: https://render.com)
- Google Gemini API Key

---

## Step-by-Step Deployment

### Step 1: Connect GitHub to Render

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Deploy an existing repository"**
4. Connect your GitHub account
5. Select your repo: `ai-course-tutor2`
6. Click **"Connect"**

### Step 2: Configure Backend Service

**Service Details:**
- Name: `ai-tutor-backend`
- Environment: `Docker`
- Plan: **Starter** (free tier)
- Auto-deploy: Enable (recommended)

**Build Settings:**
- Dockerfile: `./Dockerfile.backend`

**Environment Variables:**

| Variable | Value |
|----------|-------|
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |
| `GOOGLE_API_KEY` | *Your key from https://aistudio.google.com* |
| `API_HOST` | `0.0.0.0` |
| `API_PORT` | `8000` |

**Save and Deploy:**
- Click **"Create Web Service"**
- Render will build and deploy (5-10 minutes)
- Get backend URL (e.g., `https://ai-tutor-backend.onrender.com`)

### Step 3: Configure Frontend Service

1. Click **"New +"** → **"Web Service"** again
2. Select your repo again
3. Configure as follows:

**Service Details:**
- Name: `ai-tutor-frontend`
- Environment: `Docker`
- Plan: **Starter** (free tier)

**Build Settings:**
- Dockerfile: `./Dockerfile.frontend`

**Environment Variables:**

| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://ai-tutor-backend.onrender.com` |
| `STREAMLIT_SERVER_HEADLESS` | `true` |
| `STREAMLIT_SERVER_PORT` | `8501` |

**Save and Deploy:**
- Click **"Create Web Service"**
- Wait for deployment (5-10 minutes)
- Get frontend URL (e.g., `https://ai-tutor-frontend.onrender.com`)

### Step 4: Test Your Deployment

**Frontend:**
```
https://ai-tutor-frontend.onrender.com
```

**Backend API:**
```
https://ai-tutor-backend.onrender.com/docs
```

**Health Check:**
```
https://ai-tutor-backend.onrender.com/health
```

---

## Using render.yaml (Alternative - Automated)

If you want to automate the setup:

1. Push `render.yaml` to your repo (already included)
2. Go to Render Dashboard
3. Click **"New +"** → **"Blueprint"**
4. Select your repository
5. Render will automatically create both services from `render.yaml`
6. Add environment variables as needed

---

## Environment Variables Setup

### For Backend Service

Set these in Render dashboard for `ai-tutor-backend`:

```
ENVIRONMENT=production
LOG_LEVEL=INFO
GOOGLE_API_KEY=your_google_api_key_here
DEBUG=false
ENFORCE_HTTPS=true
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["https://ai-tutor-frontend.onrender.com"]
MAX_FILE_SIZE_MB=50
```

### For Frontend Service

Set these in Render dashboard for `ai-tutor-frontend`:

```
BACKEND_URL=https://ai-tutor-backend.onrender.com
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
```

---

## Important Notes

### Free Tier Limitations

- **Inactivity:** Services spin down after 15 minutes of inactivity
- **Memory:** 512 MB RAM (may be tight for ChromaDB)
- **Disk:** 50 GB ephemeral (data lost on redeploy)

### Production Recommendations

To avoid free tier limitations:

1. **Upgrade to Paid Plan:**
   - $7/month per service
   - Keeps services always running
   - Persistent disk storage

2. **Persistent Storage:**
   - ChromaDB data is currently in-memory
   - On free tier, data is lost when service restarts
   - For persistence, use Render's Postgres or external storage

3. **Database Setup (Optional):**
   - Create a Postgres instance on Render
   - Update connection string in environment variables
   - Allows data persistence

---

## Troubleshooting

### Service Won't Deploy

```bash
# Check logs in Render dashboard
# Click service → "Logs" tab
```

**Common issues:**
- Missing GOOGLE_API_KEY → Add it in Environment Variables
- Port already in use → Render assigns ports automatically, OK to ignore
- Memory exceeded → Upgrade to paid plan

### Frontend Can't Connect to Backend

**Solution:**
1. Get the correct backend URL from Render dashboard
2. Update `BACKEND_URL` environment variable in frontend service
3. Redeploy frontend

```
BACKEND_URL=https://ai-tutor-backend.onrender.com
```

### Service Keeps Spinning Down

**This is normal on free tier.** First request after 15 minutes will be slow (30-60 seconds).

**Solution:** Upgrade to paid plan or set up a pinging service to keep it alive.

### Out of Memory

**On free tier with 512MB:**
- ChromaDB + FastAPI + Python runtime = ~400MB
- Limited headroom for uploads
- **Solution:** Upgrade to paid plan (1GB RAM)

---

## Scaling & Performance

### Free Tier Performance
- ~10 concurrent users
- Response time: 1-3 seconds
- May timeout on large PDF uploads (>20MB)

### Paid Tier ($7/month per service)
- 1GB RAM per service
- 50+ concurrent users
- Response time: <500ms
- Supports large uploads

### For Production Scale

Consider:
- **Render Postgres** for persistent data
- **Render Redis** for caching (if needed)
- **AWS S3** for PDF storage
- **CloudFlare** for CDN

---

## Monitoring & Logs

### View Logs

1. Go to Render Dashboard
2. Click on service name
3. Select **"Logs"** tab
4. Scroll to see real-time logs

### Common Log Messages

```
✅ Startup: "Starting AI Tutor Platform (production mode)"
✅ Ready: "Application startup complete"
❌ Error: "GOOGLE_API_KEY not found" → Add environment variable
```

---

## Update & Redeploy

### Auto-Deploy (Recommended)

Every push to GitHub automatically triggers redeploy:

```bash
git add .
git commit -m "fix: update configuration"
git push origin main
# Render will automatically rebuild and deploy
```

### Manual Redeploy

1. Go to service in Render dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## Costs

### Free Plan
- $0/month per service
- Services spin down after 15 min inactivity
- 512 MB RAM
- No persistent storage

### Starter Plan
- $7/month per service
- Always running
- 512 MB RAM
- Persistent disk

### Standard Plan
- $12/month per service
- 2GB RAM
- Better performance
- Persistent disk

**Total cost for 2 services:**
- Free: $0 (with limitations)
- Starter: $14/month
- Standard: $24/month

---

## Next Steps

1. **Deploy Backend:** Follow Step 2 above
2. **Deploy Frontend:** Follow Step 3 above
3. **Test:** Access frontend URL and upload a PDF
4. **Monitor:** Watch logs in Render dashboard
5. **Upgrade:** Move to paid plan for production

---

## Support & Help

- **Render Docs:** https://render.com/docs
- **GitHub Issues:** Your repo issues
- **API Docs:** `https://your-backend-url.onrender.com/docs`

---

## Summary

| Component | URL |
|-----------|-----|
| Frontend | `https://ai-tutor-frontend.onrender.com` |
| Backend | `https://ai-tutor-backend.onrender.com` |
| API Docs | `https://ai-tutor-backend.onrender.com/docs` |
| Health | `https://ai-tutor-backend.onrender.com/health` |

**Your AI Tutor Platform is now live! 🎉**
