# Frontend Quick Start

This Streamlit app provides a simple web interface for the SHL Assessment Recommendation System.

## Local Testing

```bash
# From project root
streamlit run src/frontend/app.py
```

The app will open at http://localhost:8501

## Deployment to Streamlit Cloud

1. **Sign in to Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Deploy the app:**
   - Click "New app"
   - Repository: `gowthusaidatta/shl-assessment-recommendation-system`
   - Branch: `main`
   - Main file path: `src/frontend/app.py`
   - Click "Deploy!"

3. **Your app will be live at:**
   ```
   https://share.streamlit.io/gowthusaidatta/shl-assessment-recommendation-system/main/src/frontend/app.py
   ```

## Features

- **Natural language query input** for job descriptions
- **Real-time API integration** with the backend
- **Interactive results display** with expandable assessment details
- **CSV export** for recommendations
- **Example queries** to get started quickly

## Configuration

The API endpoint defaults to the live Render deployment:
```
https://shl-recommender-x8la.onrender.com
```

You can change this in the sidebar if testing with a local API or different deployment.
