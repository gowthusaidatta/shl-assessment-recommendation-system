# Deployment Guide

## Quick Start (Local)

### 1. Start API Server
```bash
cd C:\Users\saida\Desktop\Gpp\shl
.\.venv\Scripts\activate
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Access:** http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 2. Start Frontend
```bash
streamlit run src/frontend/app.py --server.port 8501
```

**Access:** http://localhost:8501

---

## Testing API

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Recommendations
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"I am hiring for Java developers\"}"
```

### Python Example
```python
import requests

response = requests.post(
    "http://localhost:8000/recommend",
    json={"text": "I need Python developers with teamwork skills"}
)

recommendations = response.json()["recommendations"]
for rec in recommendations:
    print(f"{rec['assessment_name']}: {rec['score']:.2f}")
```

---

## Cloud Deployment

### Option 1: Railway (Recommended)

1. **Prepare:**
```bash
# Create Procfile
echo "web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT" > Procfile

# Create runtime.txt
echo "python-3.11" > runtime.txt
```

2. **Deploy:**
- Push to GitHub
- Connect Railway to repo
- Railway auto-detects Python
- Set environment variables if needed

**URL:** `https://your-app.railway.app`

### Option 2: Google Cloud Run

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
```

2. **Deploy:**
```bash
gcloud run deploy shl-recommender \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 3: Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: shl-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
```

2. Connect GitHub repo to Render
3. Auto-deploys on push

---

## Environment Variables

If deploying with secrets:

```bash
# .env file (don't commit!)
GEMINI_API_KEY=your_key_here
USE_LLM_RERANKING=false
```

---

## Monitoring

### Health Check Endpoint
```bash
# Should return 200 OK
curl https://your-deployed-url.com/health
```

### Logs
```bash
# Railway
railway logs

# Google Cloud Run
gcloud logging read "resource.type=cloud_run_revision"
```

---

## Troubleshooting

**Issue:** Module not found  
**Fix:** Ensure all dependencies in `requirements.txt` are installed

**Issue:** FAISS index not found  
**Fix:** Run `python scripts/02_build_embeddings.py` before starting API

**Issue:** Port already in use  
**Fix:** Use different port: `--port 8001`

---

## Performance Tips

1. **Cache embeddings:** Load model once at startup (✅ already done)
2. **Async endpoints:** FastAPI handles this automatically
3. **Batch requests:** Process multiple queries together if needed
4. **CDN:** Serve frontend from CDN for faster loads

---

## Security

1. **Rate Limiting:** Add in production
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

2. **CORS:** Already configured for all origins (restrict in production)

3. **API Key:** Add authentication if needed

---

**Status:** ✅ Ready for deployment
