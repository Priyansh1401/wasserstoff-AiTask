from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Model Configuration
    SENTENCE_TRANSFORMER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LANGUAGE_MODEL: str = "google/flan-t5-base"
    
    # Vector Database Configuration
    VECTOR_DIMENSION: int = 384
    MAX_VECTORS: int = 100000
    
    # RAG Configuration
    TOP_K_RESULTS: int = 3
    RESPONSE_MAX_LENGTH: int = 150
    TEMPERATURE: float = 0.7
    
    # WordPress Configuration
    ALLOWED_ORIGINS: list = ["*"]  # Update with specific origins in production
    
    # Security
    API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
