from typing import Optional, Dict
from config import settings
import requests
from sqlalchemy.orm import Session
from models import Translation
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Service for handling translations with support for:
    - DeepL API for high-quality translations
    - Google Translate API as fallback
    - Cached translations in database
    """
    
    SUPPORTED_LANGUAGES = {
        "en": "english",
        "ru": "russian", 
        "uz": "uzbek"
    }
    
    def __init__(self):
        self.service = settings.TRANSLATION_SERVICE
        self.deepl_api_key = settings.DEEPL_API_KEY
        self.google_api_key = settings.GOOGLE_TRANSLATE_API_KEY
    
    def translate_with_deepl(
        self,
        text: str,
        source_lang: str = "EN",
        target_lang: str = "RU"
    ) -> Optional[str]:
        """
        Translate text using DeepL API.
        DeepL provides higher quality translations than Google Translate.
        
        Language codes: EN, RU, UZ (and others)
        """
        if not self.deepl_api_key:
            logger.warning("DeepL API key not configured")
            return None
        
        try:
            url = "https://api-free.deepl.com/v1/translate"
            
            params = {
                "auth_key": self.deepl_api_key,
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
            }
            
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("translations"):
                return result["translations"][0]["text"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepL API error: {str(e)}")
        
        return None
    
    def translate_with_google(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "ru"
    ) -> Optional[str]:
        """
        Translate text using Google Translate API.
        More widely available but slightly lower quality than DeepL.
        
        Requires: google-cloud-translate library
        """
        if not self.google_api_key:
            logger.warning("Google Translate API key not configured")
            return None
        
        try:
            from google.cloud import translate_v2
            
            client = translate_v2.Client(
                api_key=self.google_api_key
            )
            
            result = client.translate_text(
                text,
                source_language=source_lang,
                target_language=target_lang
            )
            
            return result.get("translatedText")
        
        except Exception as e:
            logger.error(f"Google Translate API error: {str(e)}")
        
        return None
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "ru"
    ) -> Optional[str]:
        """
        Main translation method with fallback support.
        Tries primary service first, falls back to secondary.
        """
        if self.service == "deepl":
            result = self.translate_with_deepl(text, source_lang.upper(), target_lang.upper())
            if result:
                return result
            # Fallback to Google
            return self.translate_with_google(text, source_lang, target_lang)
        else:
            result = self.translate_with_google(text, source_lang, target_lang)
            if result:
                return result
            # Fallback to DeepL
            return self.translate_with_deepl(text, source_lang.upper(), target_lang.upper())
    
    def translate_and_cache(
        self,
        db: Session,
        key: str,
        english_text: str,
        languages: list = ["ru", "uz"]
    ) -> Dict[str, str]:
        """
        Translate content and cache in database for future use.
        Reduces API calls and provides fallback for API failures.
        """
        translations = {
            "en": english_text
        }
        
        # Check if translation already exists
        existing = db.query(Translation).filter(Translation.key == key).first()
        
        if existing:
            for lang in ["en", "ru", "uz"]:
                if lang == "en":
                    translations[lang] = existing.english or english_text
                elif lang == "ru":
                    translations[lang] = existing.russian or english_text
                elif lang == "uz":
                    translations[lang] = existing.uzbek or english_text
            return translations
        
        # Create new translation and fetch
        translation_record = Translation(key=key, english=english_text)
        
        for target_lang in languages:
            translated_text = self.translate(english_text, "en", target_lang)
            if translated_text:
                if target_lang == "ru":
                    translation_record.russian = translated_text
                    translations["ru"] = translated_text
                elif target_lang == "uz":
                    translation_record.uzbek = translated_text
                    translations["uz"] = translated_text
        
        db.add(translation_record)
        db.commit()
        
        return translations
    
    def get_translations(
        self,
        db: Session,
        language: str = "en"
    ) -> Dict[str, str]:
        """
        Get all translations for a specific language.
        Used to populate i18n locale files.
        """
        translations_data = db.query(Translation).all()
        result = {}
        
        lang_attr = "english" if language == "en" else \
                   "russian" if language == "ru" else "uzbek"
        
        for trans in translations_data:
            key = trans.key
            value = getattr(trans, lang_attr) or getattr(trans, "english")
            result[key] = value
        
        return result


# Initialize service
translation_service = TranslationService()
