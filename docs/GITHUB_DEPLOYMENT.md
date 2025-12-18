# GitHub Deployment Guide

## Option 1: Local Development & Testing

### Prerequisites
- Python 3.11+
- Git
- Chrome/Chromium (for crawler)

### Setup

```bash
# Clone repository
git clone https://github.com/gowthusaidatta/shl-assessment-recommendation-system.git
cd shl-assessment-recommendation-system

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
# Terminal 1: Start API
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Frontend
streamlit run src.frontend/app.py --server.port 8501
```

Access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

---

## Option 2: GitHub Pages + External Hosting

### ⚠️ Important Note
GitHub Pages only supports **static HTML/CSS/JS**. For our FastAPI + Streamlit app, you need:

1. **API Backend**: Deploy to a cloud service (Railway, Render, Heroku, etc.)
2. **Frontend**: Can be adapted to static HTML or also hosted on same service

### Recommended: Deploy Both to Railway

#### Step 1: Prepare for Deployment

Create `Procfile` in repo root:
```
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.11
```

#### Step 2: Deploy to Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `shl-assessment-recommendation-system`
5. Railway auto-detects Python and deploys
6. Set environment variables (if needed):
   - `GEMINI_API_KEY` (already hardcoded in config)
   - `USE_LLM_RERANKING=true` (default)

Your API will be live at: `https://your-app.railway.app`

#### Step 3: Deploy Frontend Separately

Option A: Deploy Streamlit to Railway (separate service)
```bash
# In Railway, create another service from same repo
# Set start command: streamlit run src/frontend/app.py --server.port $PORT
```

Option B: Use Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Connect GitHub repo
3. Set main file: `src/frontend/app.py`
4. Deploy

Update `src/frontend/app.py` to use deployed API URL:
```python
API_URL = st.sidebar.text_input(
    "API Endpoint",
    value="https://your-app.railway.app",  # Change this
    help="URL of the recommendation API"
)
```

---

## Option 3: Docker + GitHub Container Registry

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Push

```bash
# Build
docker build -t shl-recommender .

# Tag for GitHub Container Registry
docker tag shl-recommender ghcr.io/gowthusaidatta/shl-recommender:latest

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u gowthusaidatta --password-stdin

# Push
docker push ghcr.io/gowthusaidatta/shl-recommender:latest
```

### Deploy Container

Deploy to any container hosting service:
- Google Cloud Run
- AWS ECS
- Azure Container Instances
- Railway (supports Docker)

---

## Option 4: Google Cloud Run (Free Tier Available)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Deploy
gcloud run deploy shl-recommender \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=AIzaSyBADMWw8fA1EjFmuMzgWtUMrGos2CJNUjY
```

Your API will be live at: `https://shl-recommender-xxx.run.app`

---

## Testing Your Deployed API

### Health Check
```bash
curl https://your-deployed-url/health
```

### Get Recommendations
```bash
curl -X POST https://your-deployed-url/recommend \
  -H "Content-Type: application/json" \
  -d '{"text": "I am hiring for Java developers"}'
```

### Python Test
```python
import requests

response = requests.post(
    "https://your-deployed-url/recommend",
    json={"text": "Hiring Python developers with teamwork skills"}
)

print(response.json())
```

---

## Environment Variables

If you need to change settings without modifying code:

```bash
# .env file (don't commit!)
GEMINI_API_KEY=your_key_here
USE_LLM_RERANKING=true
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Submission Checklist

For SHL submission, you need:

1. ✅ **Public GitHub Repository**
   - URL: https://github.com/gowthusaidatta/shl-assessment-recommendation-system

2. ✅ **Live API URL**
   - Deploy to Railway/Render/Cloud Run
   - Ensure `/health` and `/recommend` endpoints work
   - Test with curl/Postman

3. ✅ **Live Frontend URL**
   - Deploy Streamlit to Railway/Streamlit Cloud
   - Update API endpoint in frontend code
   - Test end-to-end flow

4. ✅ **Predictions CSV**
   - File: `data/predictions/gowthu_manikanta.csv`
   - Format: Query,Assessment_url
   - Already generated

5. ✅ **Technical Report PDF**
   - Convert `docs/TECHNICAL_REPORT.md` to PDF
   - Keep to 2 pages
   - Include architecture, evaluation, results

---

## Quick Deploy (Recommended for Submission)

### Railway (Fastest - 5 minutes)

1. Push code to GitHub
2. Go to https://railway.app
3. New Project → Deploy from GitHub
4. Select repo → Auto-deploys
5. Get URL from dashboard
6. Test `/health` endpoint

**Done!** ✅

---

## Troubleshooting

### Port Issues
Railway/Render provide `$PORT` environment variable. Code already handles this:
```python
API_PORT = int(os.getenv("PORT", 8000))
```

### Module Not Found
Ensure all files are committed to GitHub and `requirements.txt` is complete.

### FAISS Index Not Found
Make sure `data/processed/embeddings/` folder and files are in repo or rebuild:
```bash
python scripts/02_build_embeddings.py
```

### LLM Reranking Fails
If Gemini API has issues, system falls back to rule-based ranking automatically.

---

## Security Notes

⚠️ **For Production:**
- Don't hardcode API keys (use env vars)
- Enable CORS restrictions
- Add rate limiting
- Implement authentication

For this assignment submission, current setup is acceptable.

---

## Cost Considerations

- **Railway**: Free tier (500 hours/month)
- **Render**: Free tier (750 hours/month)
- **Google Cloud Run**: Free tier (2M requests/month)
- **Streamlit Cloud**: Free tier (1 app)
- **Gemini API**: Free tier (60 requests/minute)

**Estimated Cost for Assignment Period: $0** ✅

---

## Support

If deployment issues occur:
1. Check Railway/Render logs
2. Verify all dependencies installed
3. Test locally first
4. Check CORS settings for frontend
5. Ensure environment variables set

---

**Status:** Ready for deployment ✅

**Recommended Path:** Railway (API + Frontend) → Update README with live URLs → Submit
