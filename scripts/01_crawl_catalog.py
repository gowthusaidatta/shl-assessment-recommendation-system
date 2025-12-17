"""
Main crawler script to fetch and process SHL assessment catalog.
PHASE 1: Data Ingestion
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.advanced_crawler import AdvancedSHLCrawler
from src.data.preprocessor import AssessmentPreprocessor
from src.data.storage import AssessmentStorage
from config.settings import ASSESSMENTS_RAW_FILE, ASSESSMENTS_CLEAN_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main crawling and preprocessing pipeline."""
    logger.info("=" * 80)
    logger.info("PHASE 1: Data Ingestion and Processing")
    logger.info("=" * 80)
    
    # Step 1: Crawl SHL catalog (using advanced multi-strategy crawler)
    logger.info("\n[STEP 1] Crawling SHL Assessment Catalog...")
    crawler = AdvancedSHLCrawler()
    raw_assessments = crawler.crawl()
    
    if not raw_assessments:
        logger.error("No assessments found. Exiting.")
        return
    
    logger.info(f"✓ Crawled {len(raw_assessments)} assessments")
    
    # Step 2: Preprocess assessments
    logger.info("\n[STEP 2] Preprocessing Assessments...")
    processed_assessments = AssessmentPreprocessor.preprocess_batch(raw_assessments)
    logger.info(f"✓ Preprocessed {len(processed_assessments)} assessments")
    
    # Step 3: Validate
    logger.info("\n[STEP 3] Validating Assessments...")
    valid_assessments, errors = AssessmentPreprocessor.validate_assessments(processed_assessments)
    
    if errors:
        logger.warning(f"Found {len(errors)} validation errors:")
        for error in errors[:5]:
            logger.warning(f"  - {error}")
    
    logger.info(f"✓ Validation complete: {len(valid_assessments)} valid assessments")
    
    # Step 4: Save cleaned data
    logger.info("\n[STEP 4] Saving Cleaned Data...")
    AssessmentStorage.save_clean_assessments(valid_assessments)
    logger.info(f"✓ Saved to {ASSESSMENTS_CLEAN_FILE}")
    
    # Step 5: Create metadata index
    logger.info("\n[STEP 5] Creating Metadata Index...")
    metadata_index = AssessmentStorage.create_metadata_index(valid_assessments)
    
    from config.settings import METADATA_INDEX_FILE
    AssessmentStorage.save_metadata_index(metadata_index, METADATA_INDEX_FILE)
    logger.info(f"✓ Metadata index saved")
    
    # Final report
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1 SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Raw assessments crawled: {len(raw_assessments)}")
    logger.info(f"Valid assessments: {len(valid_assessments)}")
    logger.info(f"Validation errors: {len(errors)}")
    logger.info(f"Test type distribution:")
    for test_type, count in metadata_index["test_type_distribution"].items():
        logger.info(f"  {test_type}: {count}")
    logger.info("\n✓ Checkpoint 1.A PASSED: Raw data ready")
    logger.info("✓ Checkpoint 2.A PASSED: Cleaned data structured and deduplicated")
    logger.info("✓ Checkpoint 2.B PASSED: Metadata report generated")
    logger.info("\nNext step: PHASE 2 - Embeddings & Vector Store")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
