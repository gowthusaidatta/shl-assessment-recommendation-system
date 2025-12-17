"""
Evaluate recommendation system on training set.
PHASE 4: Evaluation
"""
import logging
import sys
from pathlib import Path
import pandas as pd
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import RecommendationPipeline
from src.evaluation.metrics import RecommendationMetrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_train_set() -> tuple[dict, dict]:
    """Load train set and organize by query."""
    train_file = Path("Gen_AI Dataset (1).xlsx")
    df = pd.read_excel(train_file, sheet_name="Train-Set")
    
    # Group by query
    ground_truth = defaultdict(list)
    for _, row in df.iterrows():
        query = row["Query"]
        url = row["Assessment_url"]
        ground_truth[query].append(url)
    
    queries = list(ground_truth.keys())
    logger.info(f"Loaded {len(queries)} unique queries from train set")
    
    return queries, dict(ground_truth)


def main():
    """Evaluate recommendation system."""
    logger.info("=" * 80)
    logger.info("PHASE 4: Evaluation on Train Set")
    logger.info("=" * 80)
    
    # Load train set
    logger.info("\n[STEP 1] Loading Train Set...")
    queries, ground_truth = load_train_set()
    logger.info(f"✓ Loaded {len(queries)} queries")
    
    # Initialize pipeline
    logger.info("\n[STEP 2] Initializing Pipeline...")
    pipeline = RecommendationPipeline()
    logger.info("✓ Pipeline ready")
    
    # Generate predictions
    logger.info("\n[STEP 3] Generating Predictions...")
    predictions = {}
    
    for i, query in enumerate(queries, 1):
        logger.info(f"Processing query {i}/{len(queries)}: {query[:60]}...")
        recommendations = pipeline.recommend(query, top_k=10)
        predicted_urls = [rec.url for rec in recommendations]
        predictions[query] = predicted_urls
    
    logger.info(f"✓ Generated predictions for all queries")
    
    # Evaluate
    logger.info("\n[STEP 4] Computing Metrics...")
    mean_recall, per_query_recalls = RecommendationMetrics.mean_recall_at_k(
        predictions,
        ground_truth,
        k=10
    )
    
    logger.info(f"✓ Mean Recall@10: {mean_recall:.4f}")
    
    # Detailed report
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 80)
    logger.info(f"\nMean Recall@10: {mean_recall:.2%}")
    logger.info(f"\nPer-Query Recall@10:")
    
    for query, recall in sorted(per_query_recalls.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {recall:.2%} - {query[:60]}...")
    
    # Statistics
    recalls = list(per_query_recalls.values())
    logger.info(f"\nStatistics:")
    logger.info(f"  Min Recall@10: {min(recalls):.2%}")
    logger.info(f"  Max Recall@10: {max(recalls):.2%}")
    logger.info(f"  Median Recall@10: {sorted(recalls)[len(recalls)//2]:.2%}")
    
    # Check performance threshold
    logger.info("\n" + "=" * 80)
    if mean_recall >= 0.70:
        logger.info("✓ EXCELLENT: Recall@10 ≥ 70%")
    elif mean_recall >= 0.50:
        logger.info("✓ GOOD: Recall@10 ≥ 50%")
    elif mean_recall >= 0.30:
        logger.info("○ ACCEPTABLE: Recall@10 ≥ 30%")
    else:
        logger.info("✗ NEEDS IMPROVEMENT: Recall@10 < 30%")
    
    logger.info("\n✓ Checkpoint 5.A PASSED: Baseline Recall@10 computed")
    logger.info("\nNext step: PHASE 5 - API Implementation")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
