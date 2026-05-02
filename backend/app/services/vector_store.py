import numpy as np
import pickle
import os
import logging
from typing import List, Tuple, Optional
from app.models.product import Product

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, dimension: int = 768, index_path: str = None):
        self.dimension = dimension  # Default, will be auto-detected
        self.image_dimension = 512  # CLIP image embedding dimension
        self.index_path = index_path
        self.embeddings: Optional[np.ndarray] = None
        self.image_embeddings: Optional[np.ndarray] = None  # Separate array for image embeddings
        self.product_ids: List[str] = []
        self.products: dict = {}

        if index_path and os.path.exists(f"{index_path}_meta.pkl"):
            self.load()

        logger.info(f"Vector store initialized (dimension: auto-detect, image_dim: {self.image_dimension})")

    def add_products(self, products: List[Product], embeddings: np.ndarray):
        # Auto-detect dimension from first embedding
        if self.embeddings is None and len(embeddings) > 0:
            self.dimension = embeddings.shape[1]
            logger.info(f"Auto-detected embedding dimension: {self.dimension}")
        
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            # Ensure dimensions match
            if embeddings.shape[1] != self.dimension:
                logger.warning(f"Dimension mismatch: expected {self.dimension}, got {embeddings.shape[1]}")
                # Skip products with mismatched dimensions
                valid_mask = embeddings.shape[1] == self.dimension
                embeddings = embeddings[valid_mask]
                products = [p for i, p in enumerate(products) if valid_mask[i]]
            
            if len(embeddings) > 0:
                self.embeddings = np.vstack([self.embeddings, embeddings])

        for i, product in enumerate(products):
            self.product_ids.append(product.id)
            self.products[product.id] = product

        logger.info(f"Added {len(products)} products to vector store. Total: {len(self.product_ids)}, dim: {self.dimension}")

    def add_image_embeddings(self, products: List[Product], image_embeddings: np.ndarray):
        """Add image embeddings for products"""
        if self.image_embeddings is None:
            self.image_embeddings = image_embeddings
        else:
            if image_embeddings.shape[1] != self.image_dimension:
                logger.warning(f"Image dimension mismatch: expected {self.image_dimension}, got {image_embeddings.shape[1]}")
                valid_mask = image_embeddings.shape[1] == self.image_dimension
                image_embeddings = image_embeddings[valid_mask]
                products = [p for i, p in enumerate(products) if valid_mask[i]]
            
            if len(image_embeddings) > 0:
                self.image_embeddings = np.vstack([self.image_embeddings, image_embeddings])

        for i, product in enumerate(products):
            if product.id not in self.product_ids:
                self.product_ids.append(product.id)
                self.products[product.id] = product

        logger.info(f"Added image embeddings for {len(products)} products. Total: {len(self.product_ids)}")

    def search_by_image(self, query_embedding: np.ndarray, top_k: int = 10) -> Tuple[List[Product], List[float]]:
        """Search by image embedding"""
        if self.image_embeddings is None or len(self.image_embeddings) == 0:
            return [], []

        query_embedding = np.array(query_embedding).flatten()
        
        if len(query_embedding) != self.image_dimension:
            if len(query_embedding) > self.image_dimension:
                query_embedding = query_embedding[:self.image_dimension]
            else:
                padded = np.zeros(self.image_dimension)
                padded[:len(query_embedding)] = query_embedding
                query_embedding = padded
        
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        embeddings_norm = self.image_embeddings / (
            np.linalg.norm(self.image_embeddings, axis=1, keepdims=True) + 1e-8
        )
        
        similarities = np.dot(embeddings_norm, query_norm)
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        result_scores = []
        
        for idx in top_indices:
            if similarities[idx] > 0:
                product_id = self.product_ids[idx]
                results.append(self.products[product_id])
                result_scores.append(float(similarities[idx]))

        return results, result_scores

    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> Tuple[List[Product], List[float]]:
        if self.embeddings is None or len(self.embeddings) == 0:
            return [], []

        query_embedding = np.array(query_embedding).flatten()
        
        # Handle dimension mismatch with query
        if len(query_embedding) != self.dimension:
            logger.warning(f"Query dimension mismatch: expected {self.dimension}, got {len(query_embedding)}")
            if len(query_embedding) > self.dimension:
                query_embedding = query_embedding[:self.dimension]
            else:
                # Pad with zeros
                padded = np.zeros(self.dimension)
                padded[:len(query_embedding)] = query_embedding
                query_embedding = padded
        
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        embeddings_norm = self.embeddings / (
            np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8
        )
        
        similarities = np.dot(embeddings_norm, query_norm)
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        result_scores = []
        
        for idx in top_indices:
            if similarities[idx] > 0:
                product_id = self.product_ids[idx]
                results.append(self.products[product_id])
                result_scores.append(float(similarities[idx]))

        return results, result_scores

    def save(self):
        if self.index_path and self.embeddings is not None:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            np.save(f"{self.index_path}_embeddings.npy", self.embeddings)
            with open(f"{self.index_path}_meta.pkl", "wb") as f:
                pickle.dump({
                    "product_ids": self.product_ids,
                    "products": self.products
                }, f)
            logger.info(f"Saved vector store to {self.index_path}")

    def load(self):
        if self.index_path and os.path.exists(f"{self.index_path}_meta.pkl"):
            self.embeddings = np.load(f"{self.index_path}_embeddings.npy")
            self.dimension = self.embeddings.shape[1]
            with open(f"{self.index_path}_meta.pkl", "rb") as f:
                meta = pickle.load(f)
                self.product_ids = meta["product_ids"]
                self.products = meta["products"]
            logger.info(f"Loaded vector store with {len(self.product_ids)} products, dim: {self.dimension}")


def create_vector_store(dimension: int, index_path: str) -> VectorStore:
    return VectorStore(dimension, index_path)