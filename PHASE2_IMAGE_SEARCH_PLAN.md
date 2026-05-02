# Phase 2: Image Search with CLIP - Implementation Plan

## Objective
User uploads product image → CLIP encodes → finds visually similar products in database

## Current State
- ✅ 194 products with thumbnail URLs from dummyjson
- ✅ 50 images downloaded locally (need all 194)
- ✅ sentence-transformers installed
- ⬜ CLIP not integrated yet

---

## Phased Execution Plan

### Phase 2A: Download All Product Images
**Goal:** Download all 194 product images from dummyjson

**Steps:**
1. Create script to fetch all 194 product images using existing thumbnail URLs
2. Rename files to match product IDs (prod_0001.webp, etc.)
3. Store in /data/images/
4. Verify all 194 images downloaded

**Verification:**
```bash
ls /root/projects/TSEC/data/images/ | wc -l
# Should show 194
```

---

### Phase 2B: Integrate CLIP Model
**Goal:** Add CLIP to embedding service

**Steps:**
1. Import CLIP from sentence-transformers in embedding_service.py
2. Add `self.clip_model` initialization
3. Implement `get_image_embedding(image_path)` method
4. Add `get_image_embeddings_batch()` for bulk processing

**Verification:**
```python
# Test
from app.services.embedding_service import create_embedding_service
svc = create_embedding_service('', 'all-MiniLM-L6-v2')
emb = svc.get_image_embedding_from_path('/data/images/prod_0001.webp')
len(emb)  # Should be 512 (CLIP dimension)
```

---

### Phase 2C: Generate Image Embeddings at Startup
**Goal:** Create embeddings for all product images when server starts

**Steps:**
1. Update main.py:
   - Load all 194 image files
   - Generate CLIP embeddings for each
   - Store in vector store alongside text embeddings
2. Update vector_store.py to handle image embeddings
3. Test server startup generates embeddings

**Verification:**
- Check server logs show "Generated X image embeddings"
- Test that image embeddings exist in vector store

---

### Phase 2D: Update Search Endpoint
**Goal:** Accept image upload in search and return similar products

**Steps:**
1. Update search endpoint to handle `image_data` parameter
2. When image provided:
   - If it's a path: load and encode with CLIP
   - If it's base64: decode first, then encode with CLIP
3. Search against image embeddings in vector store
4. Return visually similar products
5. Add similarity score to results

**Verification:**
```bash
# Test with sample image
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image"}'
# Should return visually similar products
```

---

### Phase 2E: Frontend Integration (Optional)
**Goal:** Add image upload button to frontend search

**Steps:**
1. Update SearchBar component to include image upload
2. Add preview for uploaded image
3. Show results when image uploaded
4. Test full flow

---

## Testing Checklist Per Phase

| Phase | Test | Success Criteria |
|-------|------|-------------------|
| 2A | `ls images/ \| wc -l` | 194 images |
| 2B | `get_image_embedding()` | Returns 512-dim vector |
| 2C | Server startup | Embeddings generated |
| 2D | Upload image to search | Returns similar products |
| 2E | Use frontend | Full flow works |

---

## Fallback Strategy

If at any phase the test fails:
1. **Phase 2A fails:** Check network, retry downloads
2. **Phase 2B fails:** Use fallback (hash-based embeddings)
3. **Phase 2C fails:** Use text embeddings as fallback
4. **Phase 2D fails:** Fall back to text search only

---

## Files to Modify

| File | Changes |
|------|---------|
| `scripts/download_all_images.py` | New - Download all 194 images |
| `backend/app/services/embedding_service.py` | Add CLIP model, get_image_embedding() |
| `backend/app/services/vector_store.py` | Handle image embeddings |
| `backend/app/main.py` | Generate image embeddings at startup |
| `backend/app/api/endpoints/search.py` | Handle image upload in search |
| `frontend/src/components/SearchBar.tsx` | Add image upload (optional) |

---

## Technical Details

### CLIP Model
- Model: `clip-ViT-B-32` (from sentence-transformers)
- Output dimension: 512
- Size: ~400MB

### Image Search Flow
```
User uploads image (base64)
        ↓
Decode base64 → PIL Image
        ↓
CLIP encodes image → 512-dim vector
        ↓
Cosine similarity with stored image embeddings
        ↓
Return top-k similar products
```

### Product Data Integration
- Products have `image_path` field pointing to local image file
- Vector store maintains separate image embeddings array
- Search can be text-only, image-only, or hybrid