import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "HackRx 6.0 Document QA API"
    API_VERSION: str = "1.0.0"
    
    # Security
    SECRET_API_KEY: str = os.getenv("SECRET_API_KEY", "hackrx-secret-key-2024")
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # PDF Processing
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    CHUNK_SIZE: int = 400  # tokens per chunk
    CHUNK_OVERLAP: int = 50  # overlap between chunks
    
    # Vector Search
    TOP_K_CHUNKS: int = 5  # number of chunks to retrieve for context
    
    # Response Configuration
    MAX_QUESTIONS: int = 10
    RESPONSE_TIMEOUT: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
