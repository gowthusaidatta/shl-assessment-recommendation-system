"""
Pydantic models for assessments and queries.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Assessment(BaseModel):
    """Model representing an SHL assessment."""
    assessment_name: str = Field(..., description="Name of the assessment")
    url: str = Field(..., description="SHL catalog URL for the assessment")
    description: Optional[str] = Field(None, description="Assessment description")
    test_type: Optional[str] = Field(None, description="Test type (K, P, Cognitive, etc.)")
    duration: Optional[str] = Field(None, description="Duration of the test")
    remote_support: Optional[bool] = Field(None, description="Whether remote support is available")
    adaptive_support: Optional[bool] = Field(None, description="Whether adaptive support is available")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Extracted keywords")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assessment_name": "Inductive Reasoning Test",
                "url": "https://www.shl.com/solutions/products/product-catalog/...",
                "description": "Assess logical reasoning abilities...",
                "test_type": "K",
                "duration": "20 minutes",
                "remote_support": True,
                "adaptive_support": False,
                "keywords": ["reasoning", "logic", "cognitive"]
            }
        }


class Recommendation(BaseModel):
    """Model representing a single recommendation."""
    assessment_name: str
    url: str
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")


class RecommendationResponse(BaseModel):
    """Response model for /recommend endpoint."""
    query: str
    recommendations: List[Recommendation] = Field(..., min_items=1, max_items=10)
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "I am hiring for Java developers...",
                "recommendations": [
                    {
                        "assessment_name": "Java Programming Test",
                        "url": "https://www.shl.com/...",
                        "score": 0.95
                    }
                ],
                "timestamp": "2025-12-17T12:00:00Z"
            }
        }


class Query(BaseModel):
    """Model representing a user query."""
    text: Optional[str] = None
    jd_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I am hiring for Java developers who can collaborate effectively..."
            }
        }


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str
    timestamp: str
    version: str
