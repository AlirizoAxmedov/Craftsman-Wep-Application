from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import get_db, engine
from models import Base
from security import decode_token
from schemas import TokenData
import logging

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Secure Quiz and Educational Platform Backend for Uzbek Kandakorlik"
)

# ============ MIDDLEWARE ============

# CORS middleware - restrict to allowed origins (security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ SECURITY ============

security = HTTPBearer()

async def get_current_user(
    request: Request
) -> TokenData:
    """
    Dependency to verify JWT token and get current user.
    Required for protected endpoints.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = auth_header.replace("Bearer ", "")
    return decode_token(token)

# ============ INCLUDE ROUTERS ============

from api.auth import router as auth_router
from api.schools import router as schools_router
from api.quizzes import router as quizzes_router
from api.translations import router as translations_router
from api.scores import router as scores_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(schools_router, prefix="/api/schools", tags=["Schools"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(translations_router, prefix="/api/translations", tags=["Translations"])
app.include_router(scores_router, prefix="/api/scores", tags=["Student Scores"])

# ============ HEALTH CHECK ============

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION
    }

# ============ ROOT ENDPOINT ============

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
