"""
Configuration management using Pydantic settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security Configuration
    API_KEYS: str = ""  # Comma-separated list of valid API keys
    MAX_DAILY_COST_USD: float = 20.0  # Daily cost limit in USD
    COST_RESET_HOUR: int = 0  # Hour (UTC) to reset daily costs
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "investment-research"
    
    # Optional: Cohere for reranking
    COHERE_API_KEY: str = ""
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 10
    RERANK_TOP_K: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Return CORS origins as a list"""
        # Base origins
        origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "https://projects.benjaminblack.consulting"
        ]
        
        # Add CORS_ORIGINS from environment variable if set (comma-separated)
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            # Split by comma and strip whitespace
            additional_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
            origins.extend(additional_origins)
        
        return origins
    
    @property
    def VALID_API_KEYS(self) -> List[str]:
        """Return list of valid API keys"""
        if not self.API_KEYS:
            return []
        return [key.strip() for key in self.API_KEYS.split(",") if key.strip()]


# Create global settings instance
settings = Settings()
