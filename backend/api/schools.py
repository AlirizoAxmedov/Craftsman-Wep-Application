from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from database import get_db
from models import School, User, UserRole
from schemas import SchoolCreate, SchoolResponse, TokenData
from security import decode_token
from typing import List

router = APIRouter()


async def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentifikatsiya talab etiladi")
    token_data = decode_token(auth_header.replace("Bearer ", ""))
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator huquqi talab etiladi")
    return user


@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new Uzbek engraving school (admin only).
    
    Examples: Bukhara, Samarkand, Fergana, Khorezm, Tashkent, Karshi
    """
    
    # Check for duplicate school
    existing = db.query(School).filter(School.slug == school_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"School with slug '{school_data.slug}' already exists"
        )
    
    new_school = School(**school_data.dict())
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    
    return new_school

@router.get("/", response_model=List[SchoolResponse])
async def list_schools(
    language: str = "en",
    db: Session = Depends(get_db)
):
    """
    List all engraving schools with multi-language support.
    
    Parameters:
    - language: 'en' (English), 'ru' (Russian), 'uz' (Uzbek)
    
    Returns schools with translated names and descriptions.
    """
    valid_languages = ["en", "ru", "uz"]
    if language not in valid_languages:
        language = "en"
    
    schools = db.query(School).all()
    
    # Format response based on language
    for school in schools:
        if language == "uz":
            school.name = school.name  # Keep Uzbek name
        elif language == "ru":
            # Use English name as fallback for Russian (can be upgraded with translations)
            school.name = f"{school.english_name} (РУ)"
        else:  # English
            school.name = school.english_name
    
    return schools

@router.get("/{school_slug}", response_model=SchoolResponse)
async def get_school(
    school_slug: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific school.
    """
    school = db.query(School).filter(School.slug == school_slug).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"School '{school_slug}' not found"
        )
    
    return school

@router.put("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    school_data: SchoolCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update school information (admin only).
    """
    school = db.query(School).filter(School.id == school_id).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    for key, value in school_data.dict(exclude_unset=True).items():
        setattr(school, key, value)
    
    db.commit()
    db.refresh(school)
    
    return school

@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a school (admin only).
    """
    school = db.query(School).filter(School.id == school_id).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    db.delete(school)
    db.commit()
