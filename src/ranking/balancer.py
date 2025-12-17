"""
Balancing and ranking logic for recommendations.
"""
import logging
from typing import List, Tuple, Dict
from collections import defaultdict
import numpy as np

from src.data.models import Assessment

logger = logging.getLogger(__name__)


class RecommendationBalancer:
    """Balance and rank recommendations based on query intent."""
    
    @staticmethod
    def score_assessment(
        assessment: Assessment,
        query_analysis: Dict,
        base_score: float
    ) -> float:
        """
        Score an assessment based on query analysis.
        Combines base semantic score with relevance adjustments.
        """
        score = base_score
        
        # Boost for matching test type
        test_type = assessment.test_type
        if test_type in query_analysis["test_type_weights"]:
            weight = query_analysis["test_type_weights"][test_type]
            score *= (1 + weight * 0.5)  # Up to 50% boost
        
        # Boost for skill keywords in description
        if assessment.keywords:
            all_skills = (query_analysis["technical_skills"] + 
                         query_analysis["behavioral_skills"])
            matching_keywords = set(assessment.keywords) & set(all_skills)
            if matching_keywords:
                keyword_boost = len(matching_keywords) * 0.1
                score *= (1 + min(keyword_boost, 0.3))  # Up to 30% boost
        
        return score
    
    @staticmethod
    def balance_by_test_type(
        candidates: List[Tuple[Assessment, float]],
        target_weights: Dict[str, float],
        top_k: int = 10
    ) -> List[Tuple[Assessment, float]]:
        """
        Balance recommendations to match target test type distribution.
        """
        # Group by test type
        by_type = defaultdict(list)
        for assessment, score in candidates:
            test_type = assessment.test_type or "Unknown"
            by_type[test_type].append((assessment, score))
        
        # Sort each group by score
        for test_type in by_type:
            by_type[test_type].sort(key=lambda x: x[1], reverse=True)
        
        # Calculate target counts
        target_counts = {}
        for test_type, weight in target_weights.items():
            target_counts[test_type] = int(top_k * weight)
        
        # Ensure we get exactly top_k items
        total_target = sum(target_counts.values())
        if total_target < top_k:
            # Add remainder to largest category
            max_type = max(target_weights, key=target_weights.get)
            target_counts[max_type] += (top_k - total_target)
        
        # Select balanced recommendations
        balanced = []
        for test_type, count in target_counts.items():
            available = by_type.get(test_type, [])
            balanced.extend(available[:count])
        
        # If we don't have enough of a specific type, fill with best from other types
        if len(balanced) < top_k:
            remaining = []
            for test_type, items in by_type.items():
                if test_type not in target_counts or target_counts[test_type] == 0:
                    remaining.extend(items)
            
            remaining.sort(key=lambda x: x[1], reverse=True)
            needed = top_k - len(balanced)
            balanced.extend(remaining[:needed])
        
        # Final sort by score and return top_k
        balanced.sort(key=lambda x: x[1], reverse=True)
        return balanced[:top_k]
    
    @staticmethod
    def deduplicate(
        recommendations: List[Tuple[Assessment, float]]
    ) -> List[Tuple[Assessment, float]]:
        """Remove duplicate assessments by URL."""
        seen_urls = set()
        unique = []
        
        for assessment, score in recommendations:
            if assessment.url not in seen_urls:
                seen_urls.add(assessment.url)
                unique.append((assessment, score))
        
        return unique
    
    @staticmethod
    def rank_and_balance(
        candidates: List[Tuple[Assessment, float]],
        query_analysis: Dict,
        top_k: int = 10,
        min_results: int = 5
    ) -> List[Tuple[Assessment, float]]:
        """
        Main ranking and balancing pipeline.
        """
        logger.info(f"Ranking {len(candidates)} candidates...")
        
        # Step 1: Re-score with query analysis
        scored = []
        for assessment, base_score in candidates:
            new_score = RecommendationBalancer.score_assessment(
                assessment, query_analysis, base_score
            )
            scored.append((assessment, new_score))
        
        # Step 2: Deduplicate
        scored = RecommendationBalancer.deduplicate(scored)
        
        # Step 3: Balance by test type if needed
        if query_analysis.get("needs_balance"):
            logger.info("Applying test type balancing...")
            scored = RecommendationBalancer.balance_by_test_type(
                scored,
                query_analysis["test_type_weights"],
                top_k
            )
        else:
            # Just sort by score
            scored.sort(key=lambda x: x[1], reverse=True)
            scored = scored[:top_k]
        
        # Ensure minimum results
        if len(scored) < min_results:
            logger.warning(f"Only {len(scored)} results, minimum is {min_results}")
        
        logger.info(f"Final recommendations: {len(scored)}")
        return scored
