import os
from typing import Optional

class DatabaseConfig:
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_TIMEOUT: int = int(os.getenv("QDRANT_TIMEOUT", "30"))

class EmbeddingConfig:
    MODEL_NAME: str = "BAAI/bge-large-en-v1.5"
    VECTOR_SIZE: int = 1024
    DISTANCE_METRIC: str = "COSINE"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

class Config:
    database = DatabaseConfig()
    embedding = EmbeddingConfig()