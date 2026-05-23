from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from database import get_db
from models import User, UserRole, StudentScore, Quiz
from schemas import UserResponse, UserCreateByAdmin, TokenData
from security import decode_token, hash_password
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


async def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentifikatsiya talab etiladi")
    token = auth_header.replace("Bearer ", "")
    token_data = decode_token(token)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator huquqi talab etiladi")
    return user


class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


@router.get("/stats")
async def get_stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {
        "total_users": db.query(User).count(),
        "students": db.query(User).filter(User.role == UserRole.STUDENT).count(),
        "teachers": db.query(User).filter(User.role == UserRole.TEACHER).count(),
        "admins": db.query(User).filter(User.role == UserRole.ADMIN).count(),
        "total_quizzes": db.query(Quiz).count(),
        "published_quizzes": db.query(Quiz).filter(Quiz.is_published == True).count(),
        "total_submissions": db.query(StudentScore).count(),
    }


@router.get("/users", response_model=List[UserResponse])
async def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreateByAdmin, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomi yoki email allaqachon mavjud")
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdateAdmin, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        if user.id == admin.id and data.role != UserRole.ADMIN:
            raise HTTPException(status_code=400, detail="O'z rolingizni o'zgartira olmaysiz")
        user.role = data.role
    if data.is_active is not None:
        if user.id == admin.id and not data.is_active:
            raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/toggle-active")
async def toggle_active(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")
    db.delete(user)
    db.commit()
