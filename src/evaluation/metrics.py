"""
Evaluation metrics for recommendation system.
"""
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class RecommendationMetrics:
    """Metrics for evaluating recommendation quality."""
    
    @staticmethod
    def recall_at_k(
        predicted_urls: List[str],
        ground_truth_urls: List[str],
        k: int = 10
    ) -> float:
        """
        Calculate Recall@K.
        
        Recall@K = (# of relevant items in top-K) / (total # of relevant items)
        """
        if not ground_truth_urls:
            return 0.0
        
        # Take only top K predictions
        top_k_predictions = set(predicted_urls[:k])
        ground_truth_set = set(ground_truth_urls)
        
        # Count matches
        matches = len(top_k_predictions & ground_truth_set)
        total_relevant = len(ground_truth_set)
        
        recall = matches / total_relevant if total_relevant > 0 else 0.0
        return recall
    
    @staticmethod
    def mean_recall_at_k(
        predictions: Dict[str, List[str]],
        ground_truth: Dict[str, List[str]],
        k: int = 10
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate Mean Recall@K across all queries.
        
        Args:
            predictions: {query: [predicted_urls]}
            ground_truth: {query: [relevant_urls]}
            k: Top-K cutoff
        
        Returns:
            (mean_recall, per_query_recalls)
        """
        per_query_recalls = {}
        
        for query in ground_truth:
            if query not in predictions:
                logger.warning(f"No predictions for query: {query}")
                per_query_recalls[query] = 0.0
                continue
            
            recall = RecommendationMetrics.recall_at_k(
                predictions[query],
                ground_truth[query],
                k
            )
            per_query_recalls[query] = recall
        
        # Calculate mean
        if per_query_recalls:
            mean_recall = sum(per_query_recalls.values()) / len(per_query_recalls)
        else:
            mean_recall = 0.0
        
        return mean_recall, per_query_recalls
    
    @staticmethod
    def precision_at_k(
        predicted_urls: List[str],
        ground_truth_urls: List[str],
        k: int = 10
    ) -> float:
        """
        Calculate Precision@K.
        
        Precision@K = (# of relevant items in top-K) / K
        """
        top_k_predictions = set(predicted_urls[:k])
        ground_truth_set = set(ground_truth_urls)
        
        matches = len(top_k_predictions & ground_truth_set)
        precision = matches / k if k > 0 else 0.0
        return precision
