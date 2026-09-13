from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional
import secrets

# Placeholder keys that have appeared in .env.example / docs. They are public,
# so a token signed with one can be forged by anyone who reads the repo.
_PLACEHOLDER_SECRETS = {
    "your-secret-key-change-this-in-production-use-a-strong-random-key-32-chars-min",
    "your-super-secret-key-change-this-to-a-random-string-at-least-32-characters-long",
    "dev-super-secret-key-change-this-to-a-random-string-at-least-32-characters-long-in-production",
}

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./kandakorlik.db"

    # JWT — no usable default: a shared default key means forgeable admin tokens.
    # Dev gets a random per-process key; production must set SECRET_KEY explicitly.
    SECRET_KEY: str = ""
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
    
    @model_validator(mode="after")
    def _enforce_secret_key(self):
        weak = (not self.SECRET_KEY) or self.SECRET_KEY in _PLACEHOLDER_SECRETS or len(self.SECRET_KEY) < 32
        if weak:
            if self.DEBUG:
                # Local dev: ephemeral key. Tokens die with the process, which is correct.
                self.SECRET_KEY = secrets.token_urlsafe(48)
            else:
                raise RuntimeError(
                    "SECRET_KEY is missing, a known placeholder, or shorter than 32 characters. "
                    "Set a strong random SECRET_KEY environment variable before starting in "
                    "production. Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
