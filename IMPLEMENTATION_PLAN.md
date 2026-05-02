# Multi-Modal Embedding Implementation Plan

## Overview
Replace current TF-IDF embeddings with proper sentence-transformers models for accurate multi-modal search.

## Current State
- Text search: TF-IDF (keyword matching, not semantic)
- Image search: Random hash (no real similarity)
- Embedding dimension: 768 (TF-IDF padded)

## Target Architecture
```
sentence-transformers (sentence-transformers library)
├── Text Model: all-MiniLM-L6-v2 (384-dim) - Fast, semantic matching
└── Image Model: clip-ViT-B-32 (512-dim) - Visual similarity

Both encode into vector space → Cosine similarity search
```

---

## Phase 1: Fix Text Embeddings

### Goal
Replace TF-IDF with sentence-transformers (all-MiniLM-L6-v2) for accurate semantic text search.

### Steps
1. Update embedding_service.py:
   - Remove TF-IDF fallback
   - Add sentence-transformers text embedding
   - Use all-MiniLM-L6-v2 model
2. Update config.py:
   - Set EMBEDDING_DIM to 384 (MiniLM output)
   - Set TEXT_EMBEDDING_MODEL to "all-MiniLM-L6-v2"
3. Rebuild product embeddings at startup with new model
4. Clear stale vector store cache
5. Test text search for accuracy

### Expected Outcome
- Text search returns semantically similar results
- "headphones" → only headphone products (not random)
- Better ranking by relevance

---

## Phase 2: Add Image Embeddings (CLIP)

### Goal
Add CLIP-based image search for visual similarity.

### Steps
1. Add CLIP model to embedding_service.py:
   - Load clip-ViT-B-32 from sentence-transformers
   - Implement get_image_embedding using CLIP
2. Update config.py:
   - Set IMAGE_EMBEDDING_DIM to 512 (CLIP output)
   - Set IMAGE_EMBEDDING_MODEL to "clip-ViT-B-32"
3. Add product image handling:
   - Store images with products OR use image URLs
   - Generate CLIP embeddings for each product image
4. Update vector store to handle dual embeddings (text + image)
5. Update search endpoint to use CLIP for image queries

### Expected Outcome
- Upload image → find visually similar products
- Sony headphone image → shows Sony/similar headphones only

---

## Phase 3: Unify Embedding Service

### Goal
Single embedding service handling both text and image modalities.

### Steps
1. Refactor embedding_service.py:
   - Unified interface for text/image embeddings
   - Lazy loading of models (load on demand)
   - Single model manager
2. Update all endpoints (search, query, recommend) to use unified service
3. Handle dimension mismatch between text (384) and image (512) embeddings

### Expected Outcome
- Clean, maintainable code
- Easy to add more modalities (voice, etc.)
- Single point of configuration

---

## Technical Details

### Dependencies (already in requirements.txt)
- sentence-transformers==2.3.1
- torch==2.1.2
- transformers==4.36.2
- pillow==10.2.0

### Models
| Model | Dim | Size | Purpose |
|-------|-----|------|---------|
| all-MiniLM-L6-v2 | 384 | ~90MB | Text embeddings |
| clip-ViT-B-32 | 512 | ~400MB | Image embeddings |

### File Changes
- backend/app/services/embedding_service.py
- backend/app/core/config.py
- backend/app/main.py
- backend/app/api/endpoints/search.py

---

## Testing Checklist

### Phase 1 Tests
- [ ] "headphones" returns only headphone products
- [ ] "gaming laptop" returns only laptops
- [ ] Similar products have higher scores

### Phase 2 Tests
- [ ] Image upload returns visually similar products
- [ ] Brand-specific images return same-brand products

### Phase 3 Tests
- [ ] Both text and image search work
- [ ] No breaking changes to existing endpoints

---

## Timeline
- Phase 1: ~30 minutes
- Phase 2: ~45 minutes  
- Phase 3: ~20 minutes
- Phase 4: ~30 minutes

Total: ~2 hours (depending on model download time)

---

## Phase 4: Integrate Real Product Data (dummyjson.com)

### Goal
Replace synthetic data with real product data from dummyjson.com API, including product images for Phase 2.

### Why dummyjson.com?
- 100+ real products with categories
- Product images included (important for visual similarity!)
- Free, no auth required
- API: `https://dummyjson.com/products`

### Steps
1. Create data loader script to fetch from dummyjson.com
2. Transform API response to our Product model format
3. Download and store product images locally
4. Update products.json with real data
5. Add image embeddings (Phase 2 prerequisite)

### Expected Outcome
- 100+ real products with actual images
- Products include: name, description, category, brand, price, rating, thumbnail images
- Data ready for Phase 2 (visual similarity)

---

## Technical Details - Phase 4

### API Endpoint
```
GET https://dummyjson.com/products
GET https://dummyjson.com/products/category/{category}
```

### Sample Product Data
```json
{
  "id": 1,
  "title": "iPhone 9",
  "description": "An apple mobile phone which is nothing like apple",
  "price": 549,
  "rating": 4.69,
  "category": "smartphones",
  "thumbnail": "https://i.dummyjson.com/data/products/1/thumbnail.jpg",
  "images": [...]
}
```

### File Changes
- scripts/fetch_products.py - New script to fetch and save products
- data/products.json - Updated with real data
- data/images/ - Store downloaded product images