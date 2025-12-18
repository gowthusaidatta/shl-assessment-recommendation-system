# Render.com Deployment Guide (Alternative to Railway)

## Why Render?
- **No image size limit** (Railway has 4GB limit causing timeouts)
- **Free tier:** 750 hours/month
- **Auto-deploys** from GitHub
- **Better Python support** for ML packages

## Deploy to Render (3 steps)

### Step 1: Disconnect Railway
- Go to Railway dashboard
- Delete the deployment (this stops the timeouts)

### Step 2: Go to Render
1. Visit https://render.com
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repo: `shl-assessment-recommendation-system`
5. Select the repository

### Step 3: Configure Service
- **Name:** `shl-recommender`
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt && python scripts/02_build_embeddings.py`
- **Start Command:** `uvicorn src.api.app:app --host 0.0.0.0 --port 8000`
- **Instance Type:** Free (0.5 CPU, 512MB RAM) - **upgradeable if needed**
- **Region:** Any

### Step 4: Deploy
- Click "Create Web Service"
- Render auto-deploys (takes ~5-10 minutes)
- Get your live URL: `https://shl-recommender.onrender.com`

## Test Your API

```bash
curl https://shl-recommender.onrender.com/health

curl -X POST https://shl-recommender.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{"text": "I need Java developers"}'
```

## Cost
- **Free:** $0 (500 hours/month is plenty)
- **If you need more:** Upgrade to $7/month paid tier

---

## Why Render Instead of Railway?
| Feature | Railway | Render |
|---------|---------|--------|
| Free Tier | 500 hrs | 750 hrs |
| Image Limit | 4 GB ⚠️ | Unlimited ✅ |
| Build Time | 30 min ⚠️ | 60 min ✅ |
| ML Libraries | Struggles | Handles well ✅ |
| Python Support | Good | Excellent ✅ |

---

## Deploy Frontend to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. **Repository:** `shl-assessment-recommendation-system`
5. **Main file path:** `src/frontend/app.py`
6. **Deploy**

Then update [src/frontend/app.py](src/frontend/app.py#L24):
```python
API_URL = st.sidebar.text_input(
    "API Endpoint",
    value="https://shl-recommender.onrender.com",  # Your Render URL
    help="URL of the recommendation API"
)
```

---

## Submission URLs
- **API:** https://shl-recommender.onrender.com
- **Frontend:** https://shl-recommender.streamlit.app (or your Render URL)
- **GitHub:** https://github.com/gowthusaidatta/shl-assessment-recommendation-system

---

**Render > Railway for ML projects.** Switch now and deploy in 5 minutes! ✅
