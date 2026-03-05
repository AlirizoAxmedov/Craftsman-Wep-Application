from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import School
from schemas import SchoolCreate, SchoolResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreate,
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
async def list_schools(db: Session = Depends(get_db)):
    """
    List all engraving schools.
    Returns basic information for each school.
    """
    schools = db.query(School).all()
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
