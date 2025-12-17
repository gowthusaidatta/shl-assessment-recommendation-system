"""
Query understanding and skill extraction module.
"""
import re
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Analyze queries to extract intent, skills, and requirements."""
    
    # Technical skills keywords
    TECHNICAL_SKILLS = {
        "java", "python", "javascript", "sql", "c++", "c#", "php", "ruby",
        "programming", "coding", "software", "developer", "engineer",
        "database", "web", "mobile", "cloud", "api", "devops",
        "machine learning", "ai", "data", "algorithm", "testing"
    }
    
    # Behavioral/soft skills keywords
    BEHAVIORAL_SKILLS = {
        "leadership", "communication", "collaboration", "teamwork",
        "interpersonal", "personality", "behavioral", "people",
        "management", "organizational", "problem solving", "critical thinking",
        "creativity", "emotional intelligence", "negotiation", "conflict",
        "customer service", "sales", "time management", "decision making"
    }
    
    # Seniority levels
    SENIORITY_LEVELS = {
        "entry": ["entry", "junior", "graduate", "new grad", "fresh"],
        "mid": ["mid", "intermediate", "professional"],
        "senior": ["senior", "lead", "principal", "expert", "advanced"]
    }
    
    @staticmethod
    def extract_skills(query: str) -> Dict[str, List[str]]:
        """Extract technical and behavioral skills from query."""
        query_lower = query.lower()
        
        technical = [skill for skill in QueryAnalyzer.TECHNICAL_SKILLS 
                    if skill in query_lower]
        behavioral = [skill for skill in QueryAnalyzer.BEHAVIORAL_SKILLS 
                     if skill in query_lower]
        
        return {
            "technical": technical,
            "behavioral": behavioral
        }
    
    @staticmethod
    def extract_seniority(query: str) -> str:
        """Extract seniority level from query."""
        query_lower = query.lower()
        
        for level, keywords in QueryAnalyzer.SENIORITY_LEVELS.items():
            if any(kw in query_lower for kw in keywords):
                return level
        
        return "mid"  # Default
    
    @staticmethod
    def infer_test_types_needed(query: str) -> Dict[str, float]:
        """
        Infer which test types (K, P) are needed and their weights.
        Returns dict like {"K": 0.6, "P": 0.4}
        """
        skills = QueryAnalyzer.extract_skills(query)
        
        technical_count = len(skills["technical"])
        behavioral_count = len(skills["behavioral"])
        
        total = technical_count + behavioral_count
        
        if total == 0:
            # Default: balanced
            return {"K": 0.5, "P": 0.5}
        
        k_weight = technical_count / total
        p_weight = behavioral_count / total
        
        # Ensure minimum representation (at least 30% each if both present)
        if k_weight > 0 and k_weight < 0.3:
            k_weight = 0.3
            p_weight = 0.7
        elif p_weight > 0 and p_weight < 0.3:
            p_weight = 0.3
            k_weight = 0.7
        
        return {"K": k_weight, "P": p_weight}
    
    @staticmethod
    def analyze(query: str) -> Dict:
        """Complete query analysis."""
        skills = QueryAnalyzer.extract_skills(query)
        seniority = QueryAnalyzer.extract_seniority(query)
        test_types = QueryAnalyzer.infer_test_types_needed(query)
        
        analysis = {
            "query": query,
            "technical_skills": skills["technical"],
            "behavioral_skills": skills["behavioral"],
            "seniority": seniority,
            "test_type_weights": test_types,
            "needs_balance": len(skills["technical"]) > 0 and len(skills["behavioral"]) > 0
        }
        
        logger.debug(f"Query analysis: {analysis}")
        return analysis
