from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import json
import logging
import os

from app.models.product import Product, ProductCreate
from app.models.schema import IngestResponse
from app.api.deps import get_config
from app.core.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter()

_embedding_service = None
_vector_store = None
_knowledge_graph = None


def get_services(settings: Settings):
    global _embedding_service, _vector_store, _knowledge_graph

    if _embedding_service is None:
        from app.services.embedding_service import create_embedding_service
        _embedding_service = create_embedding_service(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_EMBEDDING_MODEL
        )
        from app.services.vector_store import create_vector_store
        _vector_store = create_vector_store(settings.EMBEDDING_DIM, settings.INDEX_PATH)
        from app.services.graph_store import create_knowledge_graph
        _knowledge_graph = create_knowledge_graph()

    return _embedding_service, _vector_store, _knowledge_graph


@router.post("/ingest", response_model=IngestResponse)
async def ingest_products(
    products: List[ProductCreate],
    settings: Settings = Depends(get_config)
):
    """Ingest products and build index - uses cached embeddings if available"""
    try:
        embedding_service, vector_store, knowledge_graph = get_services(settings)

        logger.info(f"Ingesting {len(products)} products")

        product_objects = [Product(**p.model_dump()) for p in products]
        
        # Check if products have cached embeddings
        embeddings_to_use = []
        products_needing_embedding = []
        texts_for_embedding = []
        
        for i, product in enumerate(product_objects):
            # Check if embedding exists in the product data
            if hasattr(product, 'embedding') and product.embedding:
                embeddings_to_use.append(product.embedding)
                logger.debug(f"Using cached embedding for {product.id}")
            else:
                products_needing_embedding.append(i)
                text = f"{product.name} {product.description} {' '.join(product.features)}"
                texts_for_embedding.append(text)
        
        # Generate embeddings for products that don't have them
        if texts_for_embedding:
            logger.info(f"Generating embeddings for {len(texts_for_embedding)} products...")
            new_embeddings = embedding_service.get_text_embeddings_batch(texts_for_embedding)
            
            for idx in products_needing_embedding:
                emb_idx = products_needing_embedding.index(idx)
                embeddings_to_use.append(new_embeddings[emb_idx].tolist())
        
        # Convert to numpy array
        import numpy as np
        embeddings = np.array(embeddings_to_use)
        
        vector_store.add_products(product_objects, embeddings)
        knowledge_graph.build_from_products(product_objects, embeddings)
        vector_store.save()

        return IngestResponse(
            status="success",
            message=f"Successfully ingested {len(products)} products",
            count=len(products)
        )

    except Exception as e:
        logger.error(f"Error ingesting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/file")
async def ingest_from_file(
    file_path: str,
    settings: Settings = Depends(get_config)
):
    """Ingest products from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        products = [ProductCreate(**item) for item in data]

        return await ingest_products(products, settings)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))