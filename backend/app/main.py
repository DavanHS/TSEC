import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()
startup_services = {}

app = FastAPI(
    title="E-Commerce Product Intelligence API",
    version="1.0.0",
    description="Multi-modal RAG system for product search and recommendations"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting E-Commerce Product Intelligence API")
    await load_products_on_startup()


async def load_products_on_startup():
    """Load products from JSON into vector store on startup"""
    import json
    import os
    from app.services.embedding_service import create_embedding_service
    from app.services.vector_store import create_vector_store
    from app.services.graph_store import create_knowledge_graph
    from app.services.retriever import create_retriever
    from app.models.product import Product
    
    global startup_services
    
    products_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "products.json")
    images_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")
    if not os.path.exists(products_file):
        logger.warning(f"Products file not found: {products_file}")
        return
    
    try:
        with open(products_file, "r") as f:
            products_data = json.load(f)
        
        products = [Product(**p) for p in products_data]
        logger.info(f"Loaded {len(products)} products from JSON")
        
        # Create services
        settings = get_settings()
        embedding_service = create_embedding_service(settings.GEMINI_API_KEY, settings.EMBEDDING_MODEL)
        vector_store = create_vector_store(settings.EMBEDDING_DIM, settings.INDEX_PATH)
        knowledge_graph = create_knowledge_graph()
        retriever = create_retriever(vector_store, knowledge_graph, settings.TOP_K, 0.10)
        
        # Generate embeddings from product text using sentence-transformers
        import numpy as np
        product_texts = []
        for p in products:
            text = f"{p.name} {p.description or ''} {p.category or ''} {' '.join(p.features or [])}"
            product_texts.append(text)
        
        embeddings = embedding_service.get_text_embeddings_batch(product_texts)
        vector_store.add_products(products, embeddings)
        logger.info(f"Indexed {len(products)} products with sentence-transformers embeddings")
        
        # Generate image embeddings for all products (Phase 2C)
        if os.path.exists(images_dir):
            image_paths = []
            valid_products = []
            for p in products:
                img_path = os.path.join(images_dir, f"{p.id}.webp")
                if os.path.exists(img_path):
                    image_paths.append(img_path)
                    valid_products.append(p)
            
            if image_paths and len(valid_products) > 0:
                image_embeddings = embedding_service.get_image_embeddings_batch(image_paths)
                vector_store.add_image_embeddings(valid_products, image_embeddings)
                logger.info(f"Generated {len(valid_products)} image embeddings (CLIP)")
        
        # Store for sharing
        startup_services = {
            'embedding_service': embedding_service,
            'vector_store': vector_store,
            'knowledge_graph': knowledge_graph,
            'retriever': retriever
        }
        
    except Exception as e:
        logger.error(f"Error loading products on startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down E-Commerce Product Intelligence API")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-intelligence"}


@app.get("/")
async def root():
    return {"message": "E-Commerce Product Intelligence API"}


from app.api.endpoints import ingest, search, query, recommend

app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(recommend.router, prefix="/api/v1", tags=["recommend"])