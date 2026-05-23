from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./kandakorlik.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production-use-a-strong-random-key-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Translation API
    DEEPL_API_KEY: Optional[str] = None
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    TRANSLATION_SERVICE: str = "deepl"  # or "google"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "null",                    # file:// protocol (local HTML file)
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]
    
    # App
    APP_NAME: str = "Kandakorlik Quiz API"
    VERSION: str = "1.0.0"

    # Production frontend URL (set in Railway dashboard, e.g. https://myapp.railway.app)
    FRONTEND_URL: Optional[str] = None

    # Debug mode
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
