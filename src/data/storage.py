"""
Data storage and persistence utilities.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from src.data.models import Assessment
from config.settings import ASSESSMENTS_RAW_FILE, ASSESSMENTS_CLEAN_FILE

logger = logging.getLogger(__name__)


class AssessmentStorage:
    """Handle storage and retrieval of assessment data."""
    
    @staticmethod
    def load_raw_assessments() -> List[Dict]:
        """Load raw assessments from JSON file."""
        if not ASSESSMENTS_RAW_FILE.exists():
            logger.warning(f"Raw assessments file not found: {ASSESSMENTS_RAW_FILE}")
            return []
        
        with open(ASSESSMENTS_RAW_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} raw assessments")
        return data
    
    @staticmethod
    def load_clean_assessments() -> List[Assessment]:
        """Load cleaned assessments from JSON file."""
        if not ASSESSMENTS_CLEAN_FILE.exists():
            logger.warning(f"Clean assessments file not found: {ASSESSMENTS_CLEAN_FILE}")
            return []
        
        with open(ASSESSMENTS_CLEAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assessments = [Assessment(**item) for item in data]
        logger.info(f"Loaded {len(assessments)} clean assessments")
        return assessments
    
    @staticmethod
    def save_clean_assessments(assessments: List[Assessment]) -> None:
        """Save cleaned assessments to JSON file."""
        ASSESSMENTS_CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = [a.model_dump() for a in assessments]
        
        with open(ASSESSMENTS_CLEAN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(assessments)} clean assessments to {ASSESSMENTS_CLEAN_FILE}")
    
    @staticmethod
    def get_assessment_by_url(url: str, assessments: List[Assessment]) -> Optional[Assessment]:
        """Get assessment by URL."""
        for assessment in assessments:
            if assessment.url == url:
                return assessment
        return None
    
    @staticmethod
    def create_metadata_index(assessments: List[Assessment]) -> Dict:
        """Create metadata index for quick lookups."""
        index = {
            "total": len(assessments),
            "by_test_type": {},
            "by_name": {},
            "test_type_distribution": {}
        }
        
        for assessment in assessments:
            # By test type
            test_type = assessment.test_type or "Unknown"
            if test_type not in index["by_test_type"]:
                index["by_test_type"][test_type] = []
            index["by_test_type"][test_type].append(assessment.url)
            
            # By name
            index["by_name"][assessment.assessment_name] = assessment.url
            
            # Distribution
            index["test_type_distribution"][test_type] = index["test_type_distribution"].get(test_type, 0) + 1
        
        logger.info(f"Created metadata index: {index['test_type_distribution']}")
        return index
    
    @staticmethod
    def save_metadata_index(index: Dict, filepath: Path) -> None:
        """Save metadata index."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        
        logger.info(f"Saved metadata index to {filepath}")
