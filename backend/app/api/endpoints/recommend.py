from fastapi import APIRouter, Depends, HTTPException
import logging

from app.models.schema import RecommendRequest, RecommendResponse
from app.models.product import Product
from app.services.generator import create_generator
from app.api.deps import get_config
from app.core.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_startup_services():
    from app.main import startup_services
    return startup_services


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(
    request: RecommendRequest,
    settings: Settings = Depends(get_config)
):
    """Get product recommendations based on a product"""
    try:
        startup_services = get_startup_services()
        knowledge_graph = startup_services.get('knowledge_graph')
        vector_store = startup_services.get('vector_store')
        
        if not knowledge_graph or not vector_store:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        # Get original product
        original_product = vector_store.products.get(request.product_id)
        
        # Get category for filtering
        original_category = original_product.category if original_product else ""
        
        # Try graph-based recommendations first
        recommended_ids = knowledge_graph.get_recommendations(
            request.product_id,
            k=request.top_k or 10
        )
        
        # If no graph results, use vector similarity with category filtering
        if not recommended_ids:
            product = vector_store.products.get(request.product_id)
            if product:
                query_emb = vector_store.products[request.product_id].embedding
                if query_emb:
                    results, scores = vector_store.search(query_emb, top_k=request.top_k or 20)
                    
                    # Filter by same category (same first-level category)
                    original_cat_level1 = original_category.split(" > ")[0] if original_category else ""
                    
                    filtered = []
                    for p, s in zip(results, scores):
                        if p.id == request.product_id:
                            continue
                        p_cat_level1 = p.category.split(" > ")[0] if p.category else ""
                        
                        # Prioritize same category, but allow related categories
                        if p_cat_level1 == original_cat_level1:
                            filtered.append((p.id, s))
                        elif len(filtered) < 3:  # Allow up to 3 from related categories
                            filtered.append((p.id, s))
                    
                    recommended_ids = [pid for pid, _ in filtered[:request.top_k or 10]]
        
        recommended_products = []
        for pid in recommended_ids:
            if pid in vector_store.products:
                recommended_products.append(vector_store.products[pid])

        generator = create_generator(settings.GEMINI_API_KEY)

        if original_product and recommended_products:
            explanation = generator.generate_recommendation_response(original_product, recommended_products)
        else:
            explanation = "Based on product similarity, category, and brand relationships."

        return RecommendResponse(
            original_product_id=request.product_id,
            recommendations=recommended_products,
            explanation=explanation
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))