"""
Configuration settings for the SHL Assessment Recommendation System.
"""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = PROCESSED_DATA_DIR / "embeddings"
PREDICTIONS_DIR = DATA_DIR / "predictions"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EMBEDDINGS_DIR, PREDICTIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File paths
ASSESSMENTS_RAW_FILE = RAW_DATA_DIR / "assessments.json"
ASSESSMENTS_CLEAN_FILE = PROCESSED_DATA_DIR / "assessments_clean.json"
FAISS_INDEX_FILE = EMBEDDINGS_DIR / "faiss.index"
METADATA_INDEX_FILE = EMBEDDINGS_DIR / "metadata.json"
PREDICTIONS_CSV_FILE = PREDICTIONS_DIR / "gowthu_manikanta.csv"

# Web crawler settings
SHL_CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
CRAWL_TIMEOUT = 30  # seconds
CRAWL_RETRIES = 3
CRAWL_MIN_ASSESSMENTS = 377
CRAWL_HEADLESS = True  # Run browser in headless mode

# Embeddings settings
EMBEDDER_MODEL = "all-MiniLM-L6-v2"  # Sentence-Transformers model
EMBEDDING_DIMENSION = 384
EMBEDDER_BATCH_SIZE = 32

# Retrieval settings
RETRIEVAL_TOP_K_CANDIDATES = 50  # Initial candidates before ranking
RECOMMENDATION_TOP_K = 10  # Final recommendations
MIN_RECOMMENDATIONS = 5

# API settings
API_HOST = "0.0.0.0"
API_PORT = int(os.getenv("PORT", 8000))  # Support Railway/Render $PORT
API_TITLE = "SHL Assessment Recommendation API"
API_VERSION = "1.0.0"

# LLM settings (Gemini for optional reranking)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBADMWw8fA1EjFmuMzgWtUMrGos2CJNUjY")
# Enable by setting env var USE_LLM_RERANKING=true
USE_LLM_RERANKING = os.getenv("USE_LLM_RERANKING", "true").lower() == "true"
LLM_RERANK_TOP_K = int(os.getenv("LLM_RERANK_TOP_K", "20"))  # Only rerank top-20 candidates

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
