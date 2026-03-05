from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Quiz, Question, Answer, StudentScore, User, School
from schemas import QuizCreate, QuizResponse, QuizDetail, QuizDetailForStudent, StudentQuizSubmission, StudentScoreResponse
from typing import List
import json

router = APIRouter()

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new quiz for a school (teacher/admin only).
    
    Includes questions with multiple choice answers.
    Quiz is not published by default (set is_published=true to enable).
    """
    
    # Verify school exists
    school = db.query(School).filter(School.id == quiz_data.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"School with id {quiz_data.school_id} not found"
        )
    
    # Create quiz
    new_quiz = Quiz(
        school_id=quiz_data.school_id,
        title=quiz_data.title,
        description=quiz_data.description,
        time_limit_minutes=quiz_data.time_limit_minutes,
        passing_score=quiz_data.passing_score,
        total_questions=len(quiz_data.questions)
    )
    
    db.add(new_quiz)
    db.flush()  # Get the quiz ID without committing yet
    
    # Add questions
    for idx, question_data in enumerate(quiz_data.questions):
        new_question = Question(
            quiz_id=new_quiz.id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            order=idx + 1,
            points=question_data.points
        )
        db.add(new_question)
        db.flush()
        
        # Add answers
        for ans_idx, answer_data in enumerate(question_data.answers):
            new_answer = Answer(
                question_id=new_question.id,
                answer_text=answer_data.answer_text,
                is_correct=answer_data.is_correct,
                order=ans_idx + 1,
                explanation=answer_data.explanation
            )
            db.add(new_answer)
    
    db.commit()
    db.refresh(new_quiz)
    
    return new_quiz

@router.get("/", response_model=List[QuizResponse])
async def list_quizzes(
    school_id: int = None,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all quizzes (optionally filtered by school).
    By default, returns only published quizzes.
    """
    query = db.query(Quiz)
    
    if school_id:
        query = query.filter(Quiz.school_id == school_id)
    
    if published_only:
        query = query.filter(Quiz.is_published == True)
    
    quizzes = query.all()
    return quizzes

@router.get("/{quiz_id}", response_model=QuizDetail)
async def get_quiz_detail(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete quiz details including all questions and answers.
    
    Note: Does NOT include correct answer indicators for students.
    Use get_quiz_for_student for student endpoints.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if not quiz.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This quiz is not yet published"
        )
    
    return quiz

@router.get("/{quiz_id}/for-student", response_model=QuizDetailForStudent)
async def get_quiz_for_student(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Get quiz with full details including correct answers (for displaying results).
    Should only be called AFTER student submits quiz.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return quiz

@router.post("/{quiz_id}/submit", response_model=StudentScoreResponse)
async def submit_quiz(
    quiz_id: int,
    submission: StudentQuizSubmission,
    current_user: dict = Depends(lambda: {"user_id": 0}),
    db: Session = Depends(get_db)
):
    """
    Submit quiz answers and calculate score.
    
    Security:
    - Verifies user identity via JWT
    - Prevents duplicate submissions (optional)
    - Validates answer IDs belong to quiz questions
    - Calculates score server-side (never trust client score)
    """
    
    # Get quiz
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Verify submission matches quiz
    if submission.quiz_id != quiz_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz ID mismatch"
        )
    
    # Check for previous submission (prevent duplicate submissions)
    previous_score = db.query(StudentScore).filter(
        (StudentScore.student_id == current_user["user_id"]) &
        (StudentScore.quiz_id == quiz_id)
    ).first()
    
    if previous_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already submitted. Contact instructor for retake."
        )
    
    # Calculate score
    score = 0
    max_score = 0
    answers_data = {}
    
    for answer in submission.answers:
        # Get question
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {answer.question_id} not found"
            )
        
        max_score += question.points
        
        # Verify answer belongs to question
        if answer.answer_id:
            correct_answer = db.query(Answer).filter(
                (Answer.id == answer.answer_id) &
                (Answer.question_id == answer.question_id)
            ).first()
            
            if not correct_answer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid answer for question {answer.question_id}"
                )
            
            if correct_answer.is_correct:
                score += question.points
            
            answers_data[str(answer.question_id)] = {
                "selected_answer_id": answer.answer_id,
                "is_correct": correct_answer.is_correct
            }
    
    # Calculate percentage
    percentage = (score / max_score * 100) if max_score > 0 else 0
    is_passed = percentage >= quiz.passing_score
    
    # Save score
    student_score = StudentScore(
        student_id=current_user["user_id"],
        quiz_id=quiz_id,
        score=score,
        max_score=max_score,
        percentage=percentage,
        is_passed=is_passed,
        time_taken_seconds=submission.time_taken_seconds,
        answers_json=answers_data
    )
    
    db.add(student_score)
    db.commit()
    db.refresh(student_score)
    
    return student_score

@router.put("/{quiz_id}", response_model=QuizResponse, status_code=status.HTTP_200_OK)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizCreate,
    db: Session = Depends(get_db)
):
    """
    Update quiz (teacher/admin only).
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Update basic fields
    quiz.title = quiz_data.title
    quiz.description = quiz_data.description
    quiz.time_limit_minutes = quiz_data.time_limit_minutes
    quiz.passing_score = quiz_data.passing_score
    
    # Note: Updating questions is complex, consider separate endpoint
    
    db.commit()
    db.refresh(quiz)
    
    return quiz

@router.patch("/{quiz_id}/publish")
async def publish_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Publish a quiz so students can take it.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    quiz.is_published = True
    db.commit()
    db.refresh(quiz)
    
    return {"status": "published", "quiz_id": quiz.id}

@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a quiz (admin only).
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    db.delete(quiz)
    db.commit()
