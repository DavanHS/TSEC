from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # sentence-transformers model
    EMBEDDING_DIM: int = 384  # MiniLM-L6-v2 output dimension
    CLIP_MODEL: str = "clip-ViT-B-32"
    TOP_K: int = 10
    DATA_DIR: str = "data"
    INDEX_PATH: str = "data/faiss_index"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()