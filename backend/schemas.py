from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional, List
from models import UserRole

# ============ AUTH SCHEMAS ============

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        """Enforce strong password requirements"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserCreateByAdmin(BaseModel):
    """Schema for admin to create users with specific roles"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.STUDENT)
    
    @validator('password')
    def validate_password(cls, v):
        """Enforce strong password requirements"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: int
    username: str
    role: UserRole

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ SCHOOL SCHEMAS ============

class SchoolCreate(BaseModel):
    name: str
    english_name: str
    slug: str
    description: Optional[str] = None
    historical_period: Optional[str] = None
    distinctive_style: Optional[str] = None

class SchoolResponse(BaseModel):
    id: int
    name: str
    english_name: str
    slug: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

# ============ ANSWER SCHEMAS ============

class AnswerCreate(BaseModel):
    answer_text: str
    is_correct: bool
    order: int = 0
    explanation: Optional[str] = None

class AnswerResponse(BaseModel):
    id: int
    answer_text: str
    order: int
    explanation: Optional[str]
    
    class Config:
        from_attributes = True

class AnswerWithCorrect(AnswerResponse):
    is_correct: bool

# ============ QUESTION SCHEMAS ============

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    order: int = 0
    points: float = 1.0
    answers: List[AnswerCreate]

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    order: int
    points: float
    answers: List[AnswerResponse]
    
    class Config:
        from_attributes = True

class QuestionWithAnswers(QuestionResponse):
    answers: List[AnswerWithCorrect]

# ============ QUIZ SCHEMAS ============

class QuizCreate(BaseModel):
    school_id: int
    title: str
    description: Optional[str] = None
    time_limit_minutes: int = 30
    passing_score: float = 70.0
    questions: List[QuestionCreate]

class QuizResponse(BaseModel):
    id: int
    school_id: int
    title: str
    description: Optional[str]
    total_questions: int
    time_limit_minutes: int
    passing_score: float
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuizDetail(QuizResponse):
    questions: List[QuestionResponse]

class QuizDetailForStudent(QuizResponse):
    questions: List[QuestionWithAnswers]

# ============ STUDENT ANSWER SCHEMAS ============

class StudentAnswer(BaseModel):
    question_id: int
    answer_id: Optional[int] = None
    text_answer: Optional[str] = None

class StudentQuizSubmission(BaseModel):
    quiz_id: int
    answers: List[StudentAnswer]
    time_taken_seconds: int

# ============ SCORE SCHEMAS ============

class StudentScoreResponse(BaseModel):
    id: int
    student_id: int
    quiz_id: int
    score: float
    max_score: float
    percentage: float
    is_passed: bool
    time_taken_seconds: Optional[int]
    submitted_at: datetime
    
    class Config:
        from_attributes = True

class StudentScoreDetail(StudentScoreResponse):
    answers_json: Optional[dict]

# ============ TRANSLATION SCHEMAS ============

class TranslationCreate(BaseModel):
    key: str
    english: Optional[str] = None
    russian: Optional[str] = None
    uzbek: Optional[str] = None

class TranslationResponse(BaseModel):
    id: int
    key: str
    english: Optional[str]
    russian: Optional[str]
    uzbek: Optional[str]
    
    class Config:
        from_attributes = True

class TranslationUpdate(BaseModel):
    english: Optional[str] = None
    russian: Optional[str] = None
    uzbek: Optional[str] = None
