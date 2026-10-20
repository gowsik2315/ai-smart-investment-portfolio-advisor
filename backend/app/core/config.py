"""
Application Configuration
Loads configuration from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Smart Investment Portfolio Advisor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./investment_advisor.db"
    
    # Security
    #
    # The default below is a PLACEHOLDER and is treated as one: anything
    # starting with "your-secret-key" is rejected when DEBUG is off, so a
    # deployment cannot quietly sign real tokens with a value published
    # in .env.example. See `is_placeholder_secret`.
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Ollama AI Configuration
    #
    # Defaults match .env.example. qwen2.5:3b generates roughly 10
    # tokens/sec on CPU, so a 1000-token explanation takes ~100s; a
    # timeout below that makes every first attempt fail and succeed only
    # on retry, tripling the latency the user sees.
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_TIMEOUT: int = 180
    OLLAMA_ENABLED: bool = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_placeholder_secret(self) -> bool:
        """
        True when SECRET_KEY is still the shipped placeholder.

        The placeholder is published in .env.example, so anyone could
        forge a token signed with it. Startup checks this: a warning in
        development, a refusal to start in production.
        """
        return (
            self.SECRET_KEY.startswith("your-secret-key")
            or len(self.SECRET_KEY) < 32
        )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create global settings instance
settings = Settings()
