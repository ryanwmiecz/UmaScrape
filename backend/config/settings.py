"""
Application configuration management using environment variables.
Centralizes all configuration with validation and type safety.
"""
import os
from typing import Optional
from pathlib import Path


class Settings:
    """Application settings with environment variable support."""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # Flask settings
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", os.getenv("FLASK_PORT", "5000")))  # Render uses PORT
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    
    # CORS settings for production
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # HTTP client settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # External service URLs
    GAME8_BASE_URL: str = os.getenv(
        "GAME8_BASE_URL",
        "https://game8.co/games/Umamusume-Pretty-Derby/archives"
    )
    GAME8_RACE_LIST_URL: str = os.getenv(
        "GAME8_RACE_LIST_URL",
        "https://game8.co/games/Umamusume-Pretty-Derby/archives/536131"
    )
    DUCKDUCKGO_SEARCH_URL: str = os.getenv(
        "DUCKDUCKGO_SEARCH_URL",
        "https://html.duckduckgo.com/html/"
    )
    
    # Cache settings
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Data file paths
    CHARACTER_DATA_FILE: Path = DATA_DIR / "characters.json"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration values."""
        if cls.PORT < 1 or cls.PORT > 65535:
            raise ValueError(f"Invalid port number: {cls.PORT}")
        
        if cls.REQUEST_TIMEOUT < 1:
            raise ValueError(f"Invalid timeout: {cls.REQUEST_TIMEOUT}")
        
        if cls.LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {cls.LOG_LEVEL}")
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize settings - create directories and validate."""
        cls.ensure_directories()
        cls.validate()


# Create global settings instance
settings = Settings()
