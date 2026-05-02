import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, api_key: str, model_name: str = "all-MiniLM-L6-v2"):
        self.api_key = api_key
        self.model_name = model_name
        self.dimension = 384  # MiniLM-L6-v2 output dimension
        self.clip_dimension = 512  # CLIP ViT-B/32 output dimension
        self.text_model = None
        self.clip_model = None
        self._init_text_model()
        self._init_clip_model()

    def _init_clip_model(self):
        """Initialize CLIP model for image embeddings"""
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            if os.getenv("HF_TOKEN"):
                os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")
            
            from sentence_transformers import SentenceTransformer
            logger.info("Loading CLIP model: clip-ViT-B-32")
            self.clip_model = SentenceTransformer("clip-ViT-B-32")
            logger.info(f"Loaded CLIP model, dimension: {self.clip_dimension}")
        except Exception as e:
            logger.error(f"Could not load CLIP model: {e}")
            self.clip_model = None

    def _init_text_model(self):
        """Initialize sentence-transformers model for text embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading text embedding model: {self.model_name}")
            self.text_model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded text embedding model: {self.model_name}, dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Could not load sentence-transformers model: {e}")
            self.text_model = None

    def get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text using sentence-transformers"""
        if self.text_model is not None:
            try:
                embedding = self.text_model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error getting text embedding: {e}")
                return self._fallback_embedding(text)
        return self._fallback_embedding(text)

    def get_text_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for multiple texts"""
        if self.text_model is not None:
            try:
                embeddings = self.text_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
                logger.info(f"Generated embeddings for {len(texts)} texts, dimension: {embeddings.shape[1]}")
                return embeddings
            except Exception as e:
                logger.error(f"Error getting batch embeddings: {e}")
                return self._fallback_batch(texts)
        return self._fallback_batch(texts)

    def _fallback_embedding(self, text: str) -> List[float]:
        """Fallback random embedding"""
        import hashlib
        hash_val = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(hash_val, 16) % (2**31))
        embedding = np.random.randn(self.dimension)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()

    def _fallback_batch(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            embeddings.append(self._fallback_embedding(text))
        return np.array(embeddings)

    def get_image_embedding_from_base64(self, image_data: str) -> List[float]:
        """Get embedding for an image from base64 data"""
        if self.clip_model is None:
            return self._fallback_image_embedding(image_data)

        try:
            import base64
            from io import BytesIO
            from PIL import Image

            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes)).convert("RGB")

            embedding = self.clip_model.encode(image)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error getting image embedding from base64: {e}")
            return self._fallback_image_embedding(image_data)

    def get_image_embedding_from_path(self, image_path: str) -> List[float]:
        """Get embedding for an image from file path"""
        if self.clip_model is None:
            return self._fallback_image_embedding(image_path)

        try:
            from PIL import Image

            image = Image.open(image_path).convert("RGB")
            embedding = self.clip_model.encode(image)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error getting image embedding from path: {e}")
            return self._fallback_image_embedding(image_path)

    def get_image_embeddings_batch(self, image_paths: List[str]) -> np.ndarray:
        """Get embeddings for multiple images"""
        if self.clip_model is None:
            return self._fallback_image_batch(image_paths)

        try:
            from PIL import Image

            images = [Image.open(path).convert("RGB") for path in image_paths]
            embeddings = self.clip_model.encode(images)
            logger.info(f"Generated image embeddings for {len(image_paths)} images, dimension: {embeddings.shape[1]}")
            return embeddings
        except Exception as e:
            logger.error(f"Error getting batch image embeddings: {e}")
            return self._fallback_image_batch(image_paths)

    def _fallback_image_embedding(self, data: str) -> List[float]:
        """Fallback random embedding for images"""
        import hashlib
        hash_val = hashlib.md5(data[:100].encode()).hexdigest()
        np.random.seed(int(hash_val, 16) % (2**31))
        embedding = np.random.randn(self.clip_dimension)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()

    def _fallback_image_batch(self, paths: List[str]) -> np.ndarray:
        embeddings = []
        for path in paths:
            embeddings.append(self._fallback_image_embedding(path))
        return np.array(embeddings)

    def get_hybrid_embedding(self, text: str, image_data: str = None) -> np.ndarray:
        text_emb = np.array(self.get_text_embedding(text))

        if image_data:
            image_emb = np.array(self.get_image_embedding_from_base64(image_data))
            text_norm = text_emb / (np.linalg.norm(text_emb) + 1e-8)
            image_norm = image_emb / (np.linalg.norm(image_emb) + 1e-8)
            return 0.6 * text_norm + 0.4 * image_norm

        return text_emb


def create_embedding_service(api_key: str, model_name: str = "all-MiniLM-L6-v2") -> EmbeddingService:
    return EmbeddingService(api_key, model_name)