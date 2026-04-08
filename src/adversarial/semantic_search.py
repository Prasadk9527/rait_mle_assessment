# src/adversarial/semantic_search.py
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from src.adversarial.attack_patterns import AttackPattern
import logging

logger = logging.getLogger(__name__)

class SemanticSearch:
    """Embedding-based semantic search for attack patterns"""
    
    def __init__(self):
        logger.info("Initializing Semantic Search")
        
        try:
            logger.info("Loading embedding model: sentence-transformers/all-MiniLM-L6-v2")
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("Successfully loaded embedding model")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
        
        self.patterns = []
        self.embeddings = None
    
    def index_patterns(self, patterns: List[AttackPattern]):
        """Index attack patterns for semantic search"""
        logger.info(f"Indexing {len(patterns)} attack patterns")
        
        self.patterns = patterns
        pattern_texts = [p.prompt for p in patterns]
        
        logger.debug("Generating embeddings for attack patterns")
        self.embeddings = self.model.encode(pattern_texts)
        
        logger.info(f"Successfully indexed {len(patterns)} patterns")
        logger.debug(f"Embeddings shape: {self.embeddings.shape}")
    
    def find_similar(self, query: str, top_k: int = 3) -> List[Tuple[AttackPattern, float]]:
        """Find similar attack patterns to the query"""
        if self.embeddings is None or len(self.patterns) == 0:
            logger.warning("No patterns indexed. Call index_patterns first.")
            return []
        
        logger.debug(f"Finding similar patterns for query: {query[:100]}...")
        
        query_embedding = self.model.encode([query])[0]
        
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.5:
                results.append((self.patterns[idx], similarities[idx]))
                logger.debug(f"Match found: {self.patterns[idx].intent} (similarity: {similarities[idx]:.3f})")
        
        logger.debug(f"Found {len(results)} similar patterns")
        return results