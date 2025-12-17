"""
Embeddings module using Sentence-Transformers.
"""
import logging
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDER_MODEL, EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)


class TextEmbedder:
    """Embed text using Sentence-Transformers."""
    
    def __init__(self, model_name: str = EMBEDDER_MODEL):
        logger.info(f"Loading embedder model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = EMBEDDING_DIMENSION
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def embed(self, text: str) -> np.ndarray:
        """Embed a single text string."""
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid text for embedding: {text}")
            return np.zeros(self.dimension, dtype=np.float32)
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            return np.zeros(self.dimension, dtype=np.float32)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed a batch of texts."""
        logger.info(f"Embedding {len(texts)} texts (batch_size={batch_size})...")
        
        valid_texts = [t if isinstance(t, str) else "" for t in texts]
        
        try:
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_tensor=False
            )
            embeddings = embeddings.astype(np.float32)
            logger.info(f"Successfully embedded {len(embeddings)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding batch: {e}")
            return np.zeros((len(texts), self.dimension), dtype=np.float32)
