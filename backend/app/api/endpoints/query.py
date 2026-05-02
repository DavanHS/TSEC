from fastapi import APIRouter, Depends, HTTPException
import logging

from app.models.schema import QueryRequest, QueryResponse, SearchResult
from app.services.generator import create_generator
from app.api.deps import get_config
from app.core.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_startup_services():
    from app.main import startup_services
    return startup_services


@router.post("/query", response_model=QueryResponse)
async def query_products(
    request: QueryRequest,
    settings: Settings = Depends(get_config)
):
    """Query with RAG: get answer + recommended products"""
    try:
        startup_services = get_startup_services()
        embedding_service = startup_services.get('embedding_service')
        retriever = startup_services.get('retriever')
        
        if not embedding_service or not retriever:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        generator = create_generator(settings.GEMINI_API_KEY)

        if request.image_data:
            query_embedding = embedding_service.get_image_embedding_from_base64(
                request.image_data
            )
        else:
            query_embedding = embedding_service.get_text_embedding(request.query)

        search_results = retriever.retrieve(query_embedding, hybrid=True)

        answer = generator.generate_response(request.query, search_results)

        sources = [r.product.name for r in search_results[:3]]

        return QueryResponse(
            answer=answer,
            products=[
                SearchResult(
                    product=r.product,
                    score=r.score,
                    method=r.method
                )
                for r in search_results[:5]
            ],
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))