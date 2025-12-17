"""
Main recommendation pipeline orchestrating all components.
"""
import logging
from typing import List, Tuple, Optional
from pathlib import Path

from src.data.models import Assessment, Recommendation
from src.data.storage import AssessmentStorage
from src.embeddings.embedder import TextEmbedder
from src.retrieval.vector_store import FAISSVectorStore
from src.ranking.query_analyzer import QueryAnalyzer
from src.ranking.balancer import RecommendationBalancer
from config.settings import (
    FAISS_INDEX_FILE,
    ASSESSMENTS_CLEAN_FILE,
    RETRIEVAL_TOP_K_CANDIDATES,
    RECOMMENDATION_TOP_K,
    MIN_RECOMMENDATIONS,
    EMBEDDING_DIMENSION
)

logger = logging.getLogger(__name__)


class RecommendationPipeline:
    """End-to-end recommendation pipeline."""
    
    def __init__(self):
        logger.info("Initializing recommendation pipeline...")
        
        # Load assessments
        self.assessments = AssessmentStorage.load_clean_assessments()
        logger.info(f"Loaded {len(self.assessments)} assessments")
        
        # Initialize embedder
        self.embedder = TextEmbedder()
        
        # Load or build vector store
        if FAISS_INDEX_FILE.exists():
            logger.info("Loading existing FAISS index...")
            self.vector_store = self._load_vector_store()
        else:
            logger.warning("FAISS index not found. Building new one...")
            self.vector_store = self._build_vector_store()
        
        logger.info("Pipeline ready")
    
    def _build_vector_store(self) -> FAISSVectorStore:
        """Build vector store from scratch."""
        texts = [f"{a.assessment_name}. {a.description or ''}" 
                for a in self.assessments]
        embeddings = self.embedder.embed_batch(texts)
        
        vector_store = FAISSVectorStore(dimension=EMBEDDING_DIMENSION)
        vector_store.add_assessments(self.assessments, embeddings)
        vector_store.save(FAISS_INDEX_FILE)
        
        return vector_store
    
    def _load_vector_store(self) -> FAISSVectorStore:
        """Load vector store and sync with assessments."""
        store = FAISSVectorStore(dimension=EMBEDDING_DIMENSION)
        
        # Rebuild with current assessments
        texts = [f"{a.assessment_name}. {a.description or ''}" 
                for a in self.assessments]
        embeddings = self.embedder.embed_batch(texts)
        store.add_assessments(self.assessments, embeddings)
        
        return store
    
    def recommend(
        self,
        query: str,
        top_k: int = RECOMMENDATION_TOP_K,
        retrieve_k: int = RETRIEVAL_TOP_K_CANDIDATES
    ) -> List[Recommendation]:
        """
        Generate recommendations for a query.
        
        Args:
            query: Natural language query or job description
            top_k: Number of final recommendations (5-10)
            retrieve_k: Number of candidates to retrieve initially (50)
        
        Returns:
            List of Recommendation objects
        """
        logger.info(f"Processing query: '{query[:100]}...'")
        
        # Step 1: Analyze query
        query_analysis = QueryAnalyzer.analyze(query)
        logger.info(f"Query needs balance: {query_analysis['needs_balance']}")
        logger.info(f"Test type weights: {query_analysis['test_type_weights']}")
        
        # Step 2: Embed query
        query_embedding = self.embedder.embed(query)
        
        # Step 3: Retrieve candidates
        candidates = self.vector_store.search(query_embedding, k=retrieve_k)
        logger.info(f"Retrieved {len(candidates)} candidates")
        
        # Step 4: Rank and balance
        ranked = RecommendationBalancer.rank_and_balance(
            candidates,
            query_analysis,
            top_k=top_k,
            min_results=MIN_RECOMMENDATIONS
        )
        
        # Step 5: Convert to Recommendation objects
        recommendations = [
            Recommendation(
                assessment_name=assessment.assessment_name,
                url=assessment.url,
                score=float(score)
            )
            for assessment, score in ranked
        ]
        
        logger.info(f"Returning {len(recommendations)} recommendations")
        return recommendations


def main():
    """Test the pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    pipeline = RecommendationPipeline()
    
    # Test queries
    test_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams.",
        "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript.",
        "I need cognitive and personality tests for analyst positions"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        recommendations = pipeline.recommend(query, top_k=10)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.assessment_name} (score: {rec.score:.4f})")
            print(f"   {rec.url}")


if __name__ == "__main__":
    main()
