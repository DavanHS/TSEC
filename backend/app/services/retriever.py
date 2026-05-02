import numpy as np
from typing import List
import logging
from app.models.product import SearchResult
from app.services.vector_store import VectorStore
from app.services.graph_store import KnowledgeGraph

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(
        self,
        vector_store: VectorStore,
        knowledge_graph: KnowledgeGraph,
        top_k: int = 10,
        min_similarity: float = 0.10  # Lowered for image search with fallback embeddings
    ):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.top_k = top_k
        self.min_similarity = min_similarity

    def retrieve(
        self,
        query_embedding: np.ndarray,
        query_text: str = "",
        hybrid: bool = True
    ) -> List[SearchResult]:
        results = []

        vector_products, vector_scores = self.vector_store.search(
            query_embedding, self.top_k * 3
        )

        # Filter by similarity threshold
        for product, score in zip(vector_products, vector_scores):
            if score >= self.min_similarity:
                results.append(SearchResult(
                    product=product,
                    score=score,
                    method="vector"
                ))

        # Disable hybrid for now - it's adding unrelated products
        # Can enable later with better graph construction
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:self.top_k]

    def retrieve_by_image(
        self,
        query_embedding: np.ndarray,
    ) -> List[SearchResult]:
        """Retrieve products by image embedding similarity"""
        image_products, image_scores = self.vector_store.search_by_image(
            query_embedding, self.top_k * 3
        )

        results = []
        for product, score in zip(image_products, image_scores):
            if score >= self.min_similarity:
                results.append(SearchResult(
                    product=product,
                    score=score,
                    method="image"
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:self.top_k]

    def get_diversified_results(
        self,
        query_embedding: np.ndarray,
        diversity: float = 0.5
    ) -> List[SearchResult]:
        all_results = self.retrieve(query_embedding, hybrid=True)

        if not all_results:
            return []

        diversified = [all_results[0]]

        for result in all_results[1:]:
            last_category = diversified[-1].product.category
            if result.product.category != last_category or np.random.random() > diversity:
                diversified.append(result)
            if len(diversified) >= self.top_k:
                break

        return diversified


def create_retriever(
    vector_store: VectorStore,
    knowledge_graph: KnowledgeGraph,
    top_k: int,
    min_similarity: float = 0.35
) -> Retriever:
    return Retriever(vector_store, knowledge_graph, top_k, min_similarity)