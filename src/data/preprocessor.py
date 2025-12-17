"""
Data preprocessing and normalization utilities.
"""
import re
import logging
from typing import List, Dict, Optional

from src.data.models import Assessment

logger = logging.getLogger(__name__)


class AssessmentPreprocessor:
    """Preprocess and normalize assessment data."""
    
    # Common keywords for test type classification
    KNOWLEDGE_KEYWORDS = {
        "programming", "language", "skill", "knowledge", "test",
        "reasoning", "logical", "numerical", "verbal", "literacy",
        "java", "python", "sql", "javascript", "c++", "coding"
    }
    
    PERSONALITY_KEYWORDS = {
        "personality", "behavior", "behavioral", "people", "leadership",
        "culture", "fit", "trait", "emotional", "intelligence", "iq",
        "teamwork", "collaboration", "communication"
    }
    
    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\.,]', '', text)
        
        return text
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        if not text:
            return []
        
        # Split by common delimiters
        words = re.split(r'[\s\-,\.]+', text.lower())
        
        # Filter: keep words > 3 chars, exclude common words
        common_words = {"the", "and", "for", "that", "this", "from", "with", "you", "are", "can", "has", "your", "not"}
        keywords = [w for w in words if len(w) > 3 and w not in common_words]
        
        # Remove duplicates, preserve order
        seen = set()
        unique = []
        for word in keywords:
            if word not in seen:
                seen.add(word)
                unique.append(word)
        
        return unique[:20]  # Limit to top 20 keywords
    
    @staticmethod
    def infer_test_type(name: str, description: str, current_type: Optional[str] = None) -> Optional[str]:
        """
        Infer test type from name and description.
        Returns: K (Knowledge), P (Personality), Cognitive, or None
        """
        if current_type:
            return current_type
        
        combined_text = (name + " " + description).lower()
        
        # Check for personality indicators
        personality_count = sum(1 for keyword in AssessmentPreprocessor.PERSONALITY_KEYWORDS if keyword in combined_text)
        
        # Check for knowledge indicators
        knowledge_count = sum(1 for keyword in AssessmentPreprocessor.KNOWLEDGE_KEYWORDS if keyword in combined_text)
        
        if personality_count > knowledge_count:
            return "P"
        elif knowledge_count > personality_count:
            return "K"
        elif "reasoning" in combined_text or "cognitive" in combined_text:
            return "Cognitive"
        
        return None
    
    @staticmethod
    def preprocess_assessment(raw_assessment: Dict) -> Assessment:
        """
        Preprocess a single raw assessment dict into an Assessment model.
        """
        name = AssessmentPreprocessor.clean_text(raw_assessment.get("assessment_name", ""))
        url = raw_assessment.get("url", "").strip()
        description = AssessmentPreprocessor.clean_text(raw_assessment.get("description", ""))
        
        # Infer test type
        test_type = AssessmentPreprocessor.infer_test_type(
            name, 
            description, 
            raw_assessment.get("test_type")
        )
        
        # Extract keywords
        keywords = AssessmentPreprocessor.extract_keywords(name + " " + description)
        
        # Extract metadata
        duration = raw_assessment.get("duration")
        if duration:
            duration = AssessmentPreprocessor.clean_text(duration)
        
        assessment = Assessment(
            assessment_name=name,
            url=url,
            description=description,
            test_type=test_type,
            duration=duration,
            remote_support=raw_assessment.get("remote_support"),
            adaptive_support=raw_assessment.get("adaptive_support"),
            keywords=keywords
        )
        
        return assessment
    
    @staticmethod
    def preprocess_batch(raw_assessments: List[Dict]) -> List[Assessment]:
        """
        Preprocess a batch of raw assessments.
        """
        logger.info(f"Preprocessing {len(raw_assessments)} assessments...")
        
        processed = []
        errors = 0
        
        for i, raw in enumerate(raw_assessments):
            try:
                assessment = AssessmentPreprocessor.preprocess_assessment(raw)
                processed.append(assessment)
            except Exception as e:
                logger.warning(f"Error preprocessing assessment {i}: {e}")
                errors += 1
        
        logger.info(f"Preprocessing complete. Processed: {len(processed)}, Errors: {errors}")
        return processed
    
    @staticmethod
    def validate_assessments(assessments: List[Assessment]) -> tuple[List[Assessment], List[str]]:
        """
        Validate assessments. Return valid ones and list of errors.
        """
        valid = []
        errors = []
        
        for assessment in assessments:
            if not assessment.assessment_name or not assessment.url:
                errors.append(f"Missing name or URL: {assessment}")
                continue
            
            if not assessment.url.startswith("http"):
                errors.append(f"Invalid URL: {assessment.url}")
                continue
            
            valid.append(assessment)
        
        logger.info(f"Validation: {len(valid)} valid, {len(errors)} errors")
        return valid, errors
