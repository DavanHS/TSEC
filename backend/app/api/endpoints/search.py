from fastapi import APIRouter, Depends, HTTPException
import logging

from app.models.schema import SearchRequest, SearchResponse, SearchResult
from app.services.embedding_service import EmbeddingService
from app.services.retriever import Retriever
from app.api.deps import get_config
from app.core.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter()

_embedding_service: EmbeddingService = None
_retriever: Retriever = None


def get_services(settings: Settings):
    global _embedding_service, _retriever
    from app.main import startup_services
    if startup_services:
        return startup_services['embedding_service'], startup_services['retriever']
    return None, None


@router.post("/search", response_model=SearchResponse)
async def search_products(
    request: SearchRequest,
    settings: Settings = Depends(get_config)
):
    """Search products by text or image"""
    try:
        embedding_service, retriever = get_services(settings)
        
        if not embedding_service or not retriever:
            raise HTTPException(status_code=503, detail="Services not initialized")

        if request.image_data:
            query_embedding = embedding_service.get_image_embedding_from_base64(
                request.image_data
            )
        else:
            query_embedding = embedding_service.get_text_embedding(request.query or "")

        results = retriever.retrieve(query_embedding, hybrid=True)

        search_results = [
            SearchResult(
                product=result.product,
                score=result.score,
                method=result.method
            )
            for result in results
        ]

        return SearchResponse(
            results=search_results,
            total=len(search_results),
            query=request.query or "image search"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))