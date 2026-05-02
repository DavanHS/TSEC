import networkx as nx
import numpy as np
from typing import List, Dict, Set
import logging
from app.models.product import Product

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.product_embeddings: Dict[str, np.ndarray] = {}

    def add_product(self, product: Product, embedding: np.ndarray):
        self.graph.add_node(
            product.id,
            type="product",
            name=product.name,
            category=product.category,
            brand=product.brand,
            price=product.price,
            rating=product.rating
        )
        self.product_embeddings[product.id] = embedding

    def build_from_products(self, products: List[Product], embeddings: np.ndarray):
        logger.info(f"Building knowledge graph with {len(products)} products")

        for i, product in enumerate(products):
            self.add_product(product, embeddings[i])

        self._build_category_edges(products)
        self._build_brand_edges(products)
        self._build_similarity_edges(products, embeddings)

        logger.info(f"Graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

    def _build_category_edges(self, products: List[Product]):
        categories: Set[str] = set()

        for product in products:
            parts = product.category.split(" > ")
            for i in range(len(parts)):
                cat = " > ".join(parts[:i+1])
                if cat not in categories:
                    self.graph.add_node(cat, type="category", name=cat)
                    categories.add(cat)
                self.graph.add_edge(product.id, cat, type="belongs_to")
                if i > 0:
                    parent = " > ".join(parts[:i])
                    self.graph.add_edge(cat, parent, type="parent_of")

    def _build_brand_edges(self, products: List[Product]):
        brand_products: Dict[str, List[str]] = {}

        for product in products:
            if product.brand not in brand_products:
                brand_products[product.brand] = []
            brand_products[product.brand].append(product.id)

        for brand, prod_ids in brand_products.items():
            if len(prod_ids) > 1:
                self.graph.add_node(brand, type="brand", name=brand)
                for pid in prod_ids:
                    self.graph.add_edge(pid, brand, type="brand_of")
                for i in range(len(prod_ids)):
                    for j in range(i+1, len(prod_ids)):
                        self.graph.add_edge(
                            prod_ids[i], prod_ids[j],
                            type="same_brand", weight=0.7
                        )

    def _build_similarity_edges(self, products: List[Product], embeddings: np.ndarray):
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-8)
        similarity_matrix = np.dot(normalized, normalized.T)

        k = min(5, len(products))

        for i in range(len(products)):
            sims = similarity_matrix[i]
            top_k_indices = np.argsort(sims)[-k-1:-1][::-1]
            for j in top_k_indices:
                if sims[j] > 0.5:
                    self.graph.add_edge(
                        products[i].id,
                        products[j].id,
                        type="similar_to",
                        weight=float(sims[j])
                    )

    def get_similar_products(self, product_id: str, k: int = 5) -> List[str]:
        if product_id not in self.graph:
            return []

        similar = []
        for neighbor in self.graph.neighbors(product_id):
            edge_data = self.graph.edges[product_id, neighbor]
            if edge_data.get("type") == "similar_to":
                similar.append((neighbor, edge_data.get("weight", 0)))

        similar.sort(key=lambda x: x[1], reverse=True)
        return [pid for pid, _ in similar[:k]]

    def get_category_products(self, category: str) -> List[str]:
        products = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "product":
                if data.get("category", "").startswith(category):
                    products.append(node)
        return products

    def get_brand_products(self, brand: str) -> List[str]:
        products = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "product" and data.get("brand") == brand:
                products.append(node)
        return products

    def get_recommendations(self, product_id: str, k: int = 5) -> List[str]:
        if product_id not in self.graph:
            return []

        scores = {}

        similar = self.get_similar_products(product_id, k=10)
        for i, sid in enumerate(similar):
            scores[sid] = scores.get(sid, 0) + 0.4 * (1 - i/len(similar))

        product = self.graph.nodes[product_id]
        category = product.get("category", "")
        cat_products = self.get_category_products(category)
        for pid in cat_products:
            if pid != product_id:
                scores[pid] = scores.get(pid, 0) + 0.3

        brand = product.get("brand", "")
        brand_products = self.get_brand_products(brand)
        for pid in brand_products:
            if pid != product_id:
                scores[pid] = scores.get(pid, 0) + 0.3

        sorted_recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [pid for pid, _ in sorted_recommendations[:k]]


def create_knowledge_graph() -> KnowledgeGraph:
    return KnowledgeGraph()