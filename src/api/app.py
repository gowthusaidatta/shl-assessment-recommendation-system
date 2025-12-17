"""
FastAPI application for SHL Assessment Recommendations.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from src.data.models import Query, RecommendationResponse, HealthResponse, Recommendation
from src.pipeline import RecommendationPipeline
from config.settings import API_TITLE, API_VERSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="SHL Assessment Recommendation System using RAG"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline (loaded once at startup)
pipeline = None


@app.on_event("startup")
async def startup_event():
    """Load pipeline on startup."""
    global pipeline
    logger.info("Initializing recommendation pipeline...")
    try:
        pipeline = RecommendationPipeline()
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=API_VERSION
    )


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(query_request: Query):
    """
    Recommend assessments based on query or job description URL.
    
    Request body:
    {
        "text": "I am hiring for Java developers...",  // OR
        "jd_url": "https://example.com/job-description"
    }
    
    Response:
    {
        "query": "...",
        "recommendations": [
            {
                "assessment_name": "Java Programming Test",
                "url": "https://www.shl.com/...",
                "score": 0.95
            },
            ...
        ],
        "timestamp": "2025-12-17T12:00:00Z"
    }
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    # Extract query text
    query_text = query_request.text
    
    if not query_text and query_request.jd_url:
        # Fetch JD from URL (simplified - in production, would fetch and parse)
        raise HTTPException(
            status_code=400,
            detail="JD URL fetching not implemented. Please provide text directly."
        )
    
    if not query_text:
        raise HTTPException(
            status_code=400,
            detail="Either 'text' or 'jd_url' must be provided"
        )
    
    # Validate query length
    if len(query_text) < 10:
        raise HTTPException(
            status_code=400,
            detail="Query too short. Minimum 10 characters."
        )
    
    if len(query_text) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Query too long. Maximum 5000 characters."
        )
    
    try:
        # Generate recommendations
        recommendations = pipeline.recommend(query_text, top_k=10)
        
        # Ensure between 5-10 results
        if len(recommendations) < 5:
            logger.warning(f"Only {len(recommendations)} recommendations generated")
        
        return RecommendationResponse(
            query=query_text,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend (POST)"
        }
    }
