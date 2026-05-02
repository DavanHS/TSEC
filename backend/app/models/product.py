from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProductBase(BaseModel):
    id: str
    name: str
    description: str
    category: str
    brand: str
    price: float
    rating: float = Field(ge=0, le=5)
    features: List[str] = []
    image_path: Optional[str] = None
    embedding: Optional[List[float]] = None  # Cached 768-dim embedding


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    created_at: datetime = Field(default_factory=datetime.now)


class ProductInDB(Product):
    text_embedding: List[float]
    image_embedding: Optional[List[float]] = None


class SearchResult(BaseModel):
    product: Product
    score: float
    method: str


class QueryRequest(BaseModel):
    query: str
    image_data: Optional[str] = None
    top_k: int = 10


class QueryResponse(BaseModel):
    answer: str
    products: List[SearchResult]
    sources: List[str]