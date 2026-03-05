from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scores = relationship("StudentScore", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "Buxoro", "Samarqand"
    english_name = Column(String(100), nullable=False)  # e.g., "Bukhara", "Samarkand"
    slug = Column(String(50), unique=True, index=True)  # e.g., "bukhara"
    description = Column(Text, nullable=True)
    historical_period = Column(String(200), nullable=True)
    distinctive_style = Column(Text, nullable=True)
    
    # Relationships
    quizzes = relationship("Quiz", back_populates="school", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<School {self.english_name}>"

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_questions = Column(Integer, default=0)
    time_limit_minutes = Column(Integer, default=30)
    passing_score = Column(Float, default=70.0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    scores = relationship("StudentScore", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz {self.title}>"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="multiple_choice")  # multiple_choice, true_false, short_answer
    order = Column(Integer, default=0)
    points = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question {self.id}>"

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    explanation = Column(Text, nullable=True)  # Explanation if answer is correct/incorrect
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<Answer {self.id}>"

class StudentScore(Base):
    __tablename__ = "student_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    answers_json = Column(JSON, nullable=True)  # Store all answers as JSON
    is_passed = Column(Boolean, default=False)
    time_taken_seconds = Column(Integer, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="scores")
    quiz = relationship("Quiz", back_populates="scores")
    
    def __repr__(self):
        return f"<StudentScore {self.student_id} - {self.quiz_id}>"

class Translation(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)  # e.g., "school.bukhara.title"
    english = Column(Text, nullable=True)
    russian = Column(Text, nullable=True)
    uzbek = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Translation {self.key}>"
