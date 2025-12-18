
# SHL Assessment Recommendation System (GenAI + RAG)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-oriented, Retrieval-Augmented Generation (RAG) system for recommending **SHL Individual Test Solutions** based on natural language queries or job descriptions.



## 🎯 Overview

This system addresses the challenge of identifying the most relevant SHL assessments for a given role using semantic retrieval and structured reranking.

**Key highlights:**
- Crawled **377 Individual Test Solutions** from SHL’s public product catalog
- Semantic retrieval using FAISS and sentence embeddings
- Query understanding with skill and test-type inference
- Balanced recommendations across **Knowledge/Skills** and **Personality/Behavior**
- REST API compliant with SHL specification
- Quantitative evaluation using **Mean Recall@10**
- Lightweight Streamlit frontend for manual validation



## 🧠 System Capabilities

- Accepts:
  - Natural language queries
  - Job description text
- Returns:
  - 5–10 relevant SHL Individual Test Solutions
  - Balanced mix of technical and behavioral assessments where applicable



## 🧩 Architecture


Input Query / JD
↓
LLM Query Analysis (Gemini) - skill extraction
↓
Sentence Embedding (all-MiniLM-L6-v2)
↓
FAISS Vector Search (Top-N candidates)
↓
LLM Reranking (Gemini, optional)
↓
Rule-based Balancing & Test-Type Distribution
↓
Final Ranked Recommendations (Top-10)


## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Backend:** FastAPI
- **Embeddings:** Sentence-Transformers (all-MiniLM-L6-v2)
- **Vector Store:** FAISS
- **LLM:** Google Gemini Pro (query understanding + reranking)
- **Frontend:** Streamlit
- **Evaluation:** Mean Recall@10 (custom implementation)

## 📦 Data Collection

- **Source:** https://www.shl.com/solutions/products/product-catalog/
- Only **Individual Test Solutions** were collected
- Pre-packaged Job Solutions were explicitly excluded
- Total assessments indexed: **377**
  - Knowledge & Skills assessments
  - Personality & Behavioral assessments

All data ingestion is performed via a reproducible crawling pipeline.

## 📡 API Endpoints

### Health Check

GET /health

### Recommendation Endpoint

POST /recommend

**Request**
json
{
  "query": "Hiring a Java developer with strong collaboration skills"
}

**Response**
json
{
  "query": "...",
  "recommendations": [
    {
      "assessment_name": "...",
      "url": "...",
      "test_type": "...",
      "duration": "...",
      "remote_support": true,
      "adaptive_support": false
    }
  ]
}

The API strictly adheres to the response schema required in the assignment specification.

## 🚀 Quick Start (Local)

bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: rebuild pipeline artifacts
python scripts/01_crawl_catalog.py
python scripts/02_build_embeddings.py
python scripts/03_evaluate_train_set.py
python scripts/04_generate_test_predictions.py

# Run API
uvicorn src.api.app:app --reload

# Run frontend (separate terminal)
streamlit run src/frontend/app.py

## 📊 Evaluation

* **Metric:** Mean Recall@10
* **Dataset:** Provided labeled training queries
* **Methodology:**

  * Baseline: pure embedding-based retrieval
  * Improved: reranking with skill overlap and test-type balancing

Evaluation was used iteratively to refine retrieval quality and recommendation balance.
Detailed results and analysis are documented in the technical report.

## 📁 Project Structure
.
├── config/
├── src/
│   ├── crawler/
│   ├── data/
│   ├── embeddings/
│   ├── retrieval/
│   ├── ranking/
│   ├── evaluation/
│   ├── api/
│   ├── frontend/
│   └── pipeline.py
├── scripts/
├── data/
│   ├── raw/
│   ├── processed/
│   └── predictions/
├── docs/
│   ├── TECHNICAL_REPORT.md
│   └── DEPLOYMENT.md
├── requirements.txt
└── README.md

## 📄 Deliverables

* ✅ REST API with `/health` and `/recommend`
* ✅ Streamlit-based frontend
* ✅ CSV predictions for test set (`gowthu_manikanta.csv`)
* ✅ Technical design and evaluation report (2-page PDF)
* ✅ Fully reproducible codebase with LLM integration
* ✅ Deployment-ready (Procfile + runtime.txt)


## 🚀 Deployment

### Quick Deploy to Railway (Recommended)

1. Push to GitHub (already done ✅)
2. Go to https://railway.app
3. New Project → Deploy from GitHub
4. Select `shl-assessment-recommendation-system`
5. Railway auto-deploys in ~3 minutes

Your API will be live at: `https://your-app.railway.app`

See [docs/GITHUB_DEPLOYMENT.md](docs/GITHUB_DEPLOYMENT.md) for detailed instructions.

### Alternative Platforms
- **Render:** Free tier, auto-deploys from GitHub
- **Google Cloud Run:** Serverless, free tier available
- **Docker:** See [docs/GITHUB_DEPLOYMENT.md](docs/GITHUB_DEPLOYMENT.md) for Dockerfile

---

## 📊 Submission Files

- **Predictions CSV:** `data/predictions/gowthu_manikanta.csv` (9 queries, 89 recommendations)
- **Technical Report:** `docs/TECHNICAL_REPORT_2PAGE.md` (convert to PDF for submission)
- **GitHub Repository:** https://github.com/gowthusaidatta/shl-assessment-recommendation-system
- **API Endpoints:** Deploy and share live URL
- **Frontend:** Deploy Streamlit and share live URL

---

## 👤 Author

**Gowthu V V Satya Sai Datta Manikanta**  
SHL AI Research Intern - Take-Home Assessment  
December 2025

