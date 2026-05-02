from pydantic import BaseModel
from typing import List, Optional
from .product import Product, SearchResult as ProductSearchResult


class IngestResponse(BaseModel):
    status: str
    message: str
    count: int


class SearchRequest(BaseModel):
    query: Optional[str] = None
    image_data: Optional[str] = None
    top_k: int = 10


class SearchResult(BaseModel):
    product: Product
    score: float
    method: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


class QueryRequest(BaseModel):
    query: str
    image_data: Optional[str] = None
    top_k: int = 10


class QueryResponse(BaseModel):
    answer: str
    products: List[SearchResult]
    sources: List[str]


class RecommendRequest(BaseModel):
    product_id: str
    top_k: int = 10


class RecommendResponse(BaseModel):
    original_product_id: str
    recommendations: List[Product]
    explanation: str