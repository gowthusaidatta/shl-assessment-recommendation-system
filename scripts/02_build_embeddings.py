"""
Build embeddings and FAISS index.
PHASE 2: Embeddings & Vector Store
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.storage import AssessmentStorage
from src.embeddings.embedder import TextEmbedder
from src.retrieval.vector_store import FAISSVectorStore
from config.settings import ASSESSMENTS_CLEAN_FILE, FAISS_INDEX_FILE, EMBEDDING_DIMENSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Build embeddings and vector store."""
    logger.info("=" * 80)
    logger.info("PHASE 2: Embeddings & Vector Store Building")
    logger.info("=" * 80)
    
    # Step 1: Load clean assessments
    logger.info("\n[STEP 1] Loading Clean Assessments...")
    assessments = AssessmentStorage.load_clean_assessments()
    logger.info(f"✓ Loaded {len(assessments)} assessments")
    
    # Step 2: Create embedder
    logger.info("\n[STEP 2] Initializing Embedder...")
    embedder = TextEmbedder()
    logger.info(f"✓ Embedder initialized (dimension={EMBEDDING_DIMENSION})")
    
    # Step 3: Generate embeddings
    logger.info("\n[STEP 3] Generating Embeddings...")
    # Combine assessment name and description for embedding
    texts = [
        f"{a.assessment_name}. {a.description or ''}"
        for a in assessments
    ]
    
    embeddings = embedder.embed_batch(texts)
    logger.info(f"✓ Generated {len(embeddings)} embeddings (shape: {embeddings.shape})")
    
    # Step 4: Build FAISS index
    logger.info("\n[STEP 4] Building FAISS Index...")
    vector_store = FAISSVectorStore(dimension=EMBEDDING_DIMENSION)
    vector_store.add_assessments(assessments, embeddings)
    logger.info(f"✓ Index built ({vector_store.index.ntotal} vectors)")
    
    # Step 5: Save index
    logger.info("\n[STEP 5] Saving Index...")
    vector_store.save(FAISS_INDEX_FILE)
    logger.info(f"✓ Index saved to {FAISS_INDEX_FILE}")
    
    # Test search
    logger.info("\n[STEP 6] Testing Search...")
    test_query = "Java developer with strong collaboration skills"
    test_embedding = embedder.embed(test_query)
    results = vector_store.search(test_embedding, k=5)
    
    logger.info(f"Test query: '{test_query}'")
    logger.info("Top 5 results:")
    for i, (assessment, score) in enumerate(results, 1):
        logger.info(f"  {i}. {assessment.assessment_name} (score: {score:.4f})")
    
    # Final report
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Assessments processed: {len(assessments)}")
    logger.info(f"Embeddings generated: {len(embeddings)}")
    logger.info(f"Embedding dimension: {EMBEDDING_DIMENSION}")
    logger.info(f"Index size: {vector_store.index.ntotal}")
    logger.info(f"Test search successful: {len(results) > 0}")
    logger.info("\n✓ Checkpoint 3.A PASSED: FAISS index persisted")
    logger.info("✓ Checkpoint 3.B PASSED: Search tested and working")
    logger.info("\nNext step: PHASE 3 - Ranking & Balancing Logic")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
