"""
Generate predictions for test set.
PHASE 6: Test Set Predictions
"""
import logging
import sys
from pathlib import Path
import pandas as pd
import csv

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import RecommendationPipeline
from config.settings import PREDICTIONS_CSV_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_test_queries() -> list:
    """Load test queries from Excel."""
    test_file = Path("Gen_AI Dataset (1).xlsx")
    df = pd.read_excel(test_file, sheet_name="Test-Set")
    queries = df["Query"].tolist()
    logger.info(f"Loaded {len(queries)} test queries")
    return queries


def main():
    """Generate test predictions and save to CSV."""
    logger.info("=" * 80)
    logger.info("PHASE 6: Test Set Predictions")
    logger.info("=" * 80)
    
    # Load test queries
    logger.info("\n[STEP 1] Loading Test Queries...")
    test_queries = load_test_queries()
    logger.info(f"✓ Loaded {len(test_queries)} queries")
    
    # Initialize pipeline
    logger.info("\n[STEP 2] Initializing Pipeline...")
    pipeline = RecommendationPipeline()
    logger.info("✓ Pipeline ready")
    
    # Generate predictions
    logger.info("\n[STEP 3] Generating Predictions...")
    all_predictions = []
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"Processing query {i}/{len(test_queries)}: {query[:60]}...")
        recommendations = pipeline.recommend(query, top_k=10)
        
        for rec in recommendations:
            all_predictions.append({
                "Query": query,
                "Assessment_url": rec.url
            })
        
        logger.info(f"  Generated {len(recommendations)} recommendations")
    
    logger.info(f"✓ Total predictions: {len(all_predictions)}")
    
    # Save to CSV
    logger.info("\n[STEP 4] Saving to CSV...")
    PREDICTIONS_CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(PREDICTIONS_CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Query", "Assessment_url"])
        writer.writeheader()
        writer.writerows(all_predictions)
    
    logger.info(f"✓ Saved to {PREDICTIONS_CSV_FILE}")
    
    # Final report
    logger.info("\n" + "=" * 80)
    logger.info("PREDICTIONS SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Test queries: {len(test_queries)}")
    logger.info(f"Total predictions: {len(all_predictions)}")
    logger.info(f"Avg per query: {len(all_predictions) / len(test_queries):.1f}")
    logger.info(f"Output file: {PREDICTIONS_CSV_FILE}")
    logger.info("\n✓ Checkpoint 7.A PASSED: Test predictions CSV generated")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
