from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Translation
from schemas import TranslationCreate, TranslationResponse, TranslationUpdate
from translations import translation_service
from typing import List, Dict

router = APIRouter()

@router.post("/", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def create_translation(
    translation_data: TranslationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new translation entry manually or via API.
    """
    # Check for duplicate key
    existing = db.query(Translation).filter(Translation.key == translation_data.key).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Translation key '{translation_data.key}' already exists"
        )
    
    new_translation = Translation(**translation_data.dict())
    db.add(new_translation)
    db.commit()
    db.refresh(new_translation)
    
    return new_translation

@router.post("/{key}/auto-translate")
async def auto_translate(
    key: str,
    english_text: str,
    languages: List[str] = ["ru", "uz"],
    db: Session = Depends(get_db)
):
    """
    Automatically translate content to specified languages using DeepL/Google API.
    
    Process:
    1. Accepts English text
    2. Calls translation service to translate to Russian, Uzbek
    3. Caches results in database
    4. Returns translations dictionary
    """
    translations = translation_service.translate_and_cache(
        db,
        key=key,
        english_text=english_text,
        languages=languages
    )
    
    return {
        "key": key,
        "translations": translations
    }

@router.get("/locale/{language}")
async def get_locale_file(
    language: str,
    db: Session = Depends(get_db)
):
    """
    Get entire translation file for specific language.
    Used by frontend i18n to load locale file.
    
    Language codes: en, ru, uz
    Returns: Dictionary of key -> translated_text
    
    Example response:
    {
      "school.bukhara.title": "Bukhara School",
      "school.bukhara.description": "...",
      "quiz.instructions": "..."
    }
    """
    valid_languages = ["en", "ru", "uz"]
    
    if language not in valid_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language must be one of: {', '.join(valid_languages)}"
        )
    
    translations = translation_service.get_translations(db, language)
    
    return {
        "language": language,
        "translations": translations
    }

@router.get("/", response_model=List[TranslationResponse])
async def list_translations(
    key_prefix: str = None,
    db: Session = Depends(get_db)
):
    """
    List all translation entries, optionally filtered by key prefix.
    
    Examples:
    - /api/translations/?key_prefix=school
    - /api/translations/ (all)
    """
    query = db.query(Translation)
    
    if key_prefix:
        query = query.filter(Translation.key.startswith(key_prefix))
    
    translations = query.order_by(Translation.key).all()
    return translations

@router.get("/{key}", response_model=TranslationResponse)
async def get_translation(
    key: str,
    db: Session = Depends(get_db)
):
    """
    Get specific translation entry.
    """
    translation = db.query(Translation).filter(Translation.key == key).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Translation key '{key}' not found"
        )
    
    return translation

@router.put("/{key}", response_model=TranslationResponse)
async def update_translation(
    key: str,
    translation_data: TranslationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update translation entries for specific key.
    """
    translation = db.query(Translation).filter(Translation.key == key).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Translation key '{key}' not found"
        )
    
    for field, value in translation_data.dict(exclude_unset=True).items():
        setattr(translation, field, value)
    
    db.commit()
    db.refresh(translation)
    
    return translation

@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation(
    key: str,
    db: Session = Depends(get_db)
):
    """
    Delete translation entry.
    """
    translation = db.query(Translation).filter(Translation.key == key).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Translation key '{key}' not found"
        )
    
    db.delete(translation)
    db.commit()

@router.post("/batch/import")
async def batch_import_translations(
    translations_data: List[TranslationCreate],
    db: Session = Depends(get_db)
):
    """
    Batch import multiple translations.
    Useful for loading from JSON files or initial setup.
    """
    imported_count = 0
    skipped_count = 0
    
    for trans_data in translations_data:
        existing = db.query(Translation).filter(
            Translation.key == trans_data.key
        ).first()
        
        if existing:
            skipped_count += 1
            continue
        
        new_translation = Translation(**trans_data.dict())
        db.add(new_translation)
        imported_count += 1
    
    db.commit()
    
    return {
        "imported": imported_count,
        "skipped": skipped_count
    }
