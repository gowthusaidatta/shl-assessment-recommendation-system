"""
Vector store using FAISS for efficient similarity search.
"""
import logging
import json
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
import faiss

from src.data.models import Assessment
from config.settings import FAISS_INDEX_FILE, METADATA_INDEX_FILE

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store for assessments."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance
        self.assessments: List[Assessment] = []
        self.id_to_assessment: dict = {}  # vector_id -> Assessment
        logger.info(f"Initialized FAISS index (dimension={dimension})")
    
    def add_assessments(self, assessments: List[Assessment], embeddings: np.ndarray) -> None:
        """Add assessments and their embeddings to the index."""
        if len(assessments) != len(embeddings):
            raise ValueError(f"Mismatch: {len(assessments)} assessments, {len(embeddings)} embeddings")
        
        logger.info(f"Adding {len(assessments)} assessments to index...")
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype(np.float32)
        
        # Add vectors to FAISS index
        self.index.add(embeddings)
        
        # Store assessment references
        for idx, assessment in enumerate(assessments):
            vector_id = len(self.assessments) + idx
            self.assessments.append(assessment)
            self.id_to_assessment[vector_id] = assessment
        
        logger.info(f"Index now contains {self.index.ntotal} vectors")
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[Assessment, float]]:
        """
        Search for top-k nearest neighbors.
        Returns list of (Assessment, distance) tuples.
        """
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        query_embedding = query_embedding.astype(np.float32)
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx in self.id_to_assessment:
                assessment = self.id_to_assessment[idx]
                # Convert L2 distance to similarity score (higher = better)
                # Using exp(-distance) for smooth conversion
                score = float(np.exp(-dist))
                results.append((assessment, score))
        
        return results
    
    def save(self, filepath: Path) -> None:
        """Save index to disk."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving FAISS index to {filepath}")
        faiss.write_index(self.index, str(filepath))
        
        # Also save assessment references as JSON
        metadata_file = filepath.parent / "assessments_metadata.json"
        metadata = {
            str(idx): {
                "name": assessment.assessment_name,
                "url": assessment.url,
                "test_type": assessment.test_type
            }
            for idx, assessment in self.id_to_assessment.items()
        }
        
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved index and metadata")
    
    @classmethod
    def load(cls, filepath: Path) -> "FAISSVectorStore":
        """Load index from disk."""
        logger.info(f"Loading FAISS index from {filepath}")
        
        index = faiss.read_index(str(filepath))
        dimension = index.d
        
        store = cls(dimension=dimension)
        store.index = index
        
        # Load assessment metadata
        metadata_file = filepath.parent / "assessments_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # Rebuild assessments list (placeholder - need full data)
            for idx_str, data in metadata.items():
                idx = int(idx_str)
                assessment = Assessment(
                    assessment_name=data["name"],
                    url=data["url"],
                    test_type=data.get("test_type")
                )
                store.assessments.append(assessment)
                store.id_to_assessment[idx] = assessment
        
        logger.info(f"Loaded index with {store.index.ntotal} vectors")
        return store
