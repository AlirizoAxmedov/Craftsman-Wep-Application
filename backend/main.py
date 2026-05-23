from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.requests import Request
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import get_db, engine
from models import Base
from security import decode_token
from schemas import TokenData
import logging
import os
import mimetypes

mimetypes.add_type('video/mp4', '.MOV')
mimetypes.add_type('video/mp4', '.mov')

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="O'zbek Kandakorlik platformasi backend API"
)

_allowed_origins = list(settings.ALLOWED_ORIGINS)
if settings.FRONTEND_URL:
    _allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.railway\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Content-Length"],
    max_age=600,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for folder in ["Images", "Cities", "Patterns", "Schools", "Videos", "Naqshlar"]:
    folder_path = os.path.join(BASE_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)
    app.mount(f"/static/{folder.lower()}", StaticFiles(directory=folder_path), name=folder.lower())
    app.mount(f"/{folder}", StaticFiles(directory=folder_path), name=f"{folder.lower()}-direct")
    app.mount(f"/{folder.lower()}", StaticFiles(directory=folder_path), name=f"{folder.lower()}-lower")


async def get_current_user(request: Request) -> TokenData:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = auth_header.replace("Bearer ", "")
    return decode_token(token)


from api.auth import router as auth_router
from api.schools import router as schools_router
from api.quizzes import router as quizzes_router
from api.scores import router as scores_router
from api.admin import router as admin_router

app.include_router(auth_router, prefix="/api/auth", tags=["Autentifikatsiya"])
app.include_router(schools_router, prefix="/api/schools", tags=["Maktablar"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["Testlar"])
app.include_router(scores_router, prefix="/api/scores", tags=["Natijalar"])
app.include_router(admin_router, prefix="/api/admin", tags=["Administrator"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.VERSION}


@app.get("/")
async def serve_frontend():
    html_path = os.path.join(BASE_DIR, "Craftsman2.html")
    return FileResponse(html_path, media_type="text/html")


@app.get("/Craftsman2.html")
async def serve_frontend_alias():
    html_path = os.path.join(BASE_DIR, "Craftsman2.html")
    return FileResponse(html_path, media_type="text/html")


@app.get("/api-config.js")
async def serve_api_config():
    js_path = os.path.join(BASE_DIR, "api-config.js")
    return FileResponse(js_path, media_type="application/javascript")


@app.get("/api")
async def root():
    return {"message": f"{settings.APP_NAME} ga xush kelibsiz", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
