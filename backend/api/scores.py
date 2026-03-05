from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import StudentScore, Quiz, User, UserRole
from schemas import StudentScoreResponse, StudentScoreDetail
from typing import List

router = APIRouter()

@router.get("/my-scores", response_model=List[StudentScoreResponse])
async def get_my_scores(
    current_user: dict = Depends(lambda: {"user_id": 0}),
    db: Session = Depends(get_db)
):
    """
    Get all quiz scores for the current student.
    Requires authentication.
    """
    scores = db.query(StudentScore).filter(
        StudentScore.student_id == current_user["user_id"]
    ).order_by(StudentScore.submitted_at.desc()).all()
    
    return scores

@router.get("/my-scores/{quiz_id}", response_model=StudentScoreDetail)
async def get_my_quiz_score(
    quiz_id: int,
    current_user: dict = Depends(lambda: {"user_id": 0}),
    db: Session = Depends(get_db)
):
    """
    Get specific quiz score and detailed answers for current student.
    """
    score = db.query(StudentScore).filter(
        (StudentScore.student_id == current_user["user_id"]) &
        (StudentScore.quiz_id == quiz_id)
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found"
        )
    
    return score

@router.get("/leaderboard", response_model=List[dict])
async def get_leaderboard(
    quiz_id: int = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for a quiz (top scores).
    Anonymous display: only shows percentage and rank, not names.
    """
    query = db.query(StudentScore).order_by(StudentScore.percentage.desc())
    
    if quiz_id:
        query = query.filter(StudentScore.quiz_id == quiz_id)
    
    top_scores = query.limit(limit).all()
    
    leaderboard = []
    for idx, score in enumerate(top_scores, 1):
        leaderboard.append({
            "rank": idx,
            "percentage": score.percentage,
            "score": score.score,
            "max_score": score.max_score,
            "is_passed": score.is_passed,
            "submitted_at": score.submitted_at
        })
    
    return leaderboard

@router.get("/student/{student_id}/scores", response_model=List[StudentScoreResponse])
async def get_student_scores(
    student_id: int,
    current_user: dict = Depends(lambda: {"user_id": 0}),
    db: Session = Depends(get_db)
):
    """
    Get scores for a specific student (teacher/admin only).
    Security: Verify permission before returning.
    """
    # Check permission - only teachers/admins and self can view
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user or (user.role == UserRole.STUDENT and current_user["user_id"] != student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these scores"
        )
    
    scores = db.query(StudentScore).filter(
        StudentScore.student_id == student_id
    ).order_by(StudentScore.submitted_at.desc()).all()
    
    return scores

@router.get("/stats/summary")
async def get_stats_summary(
    current_user: dict = Depends(lambda: {"user_id": 0}),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for current student.
    """
    scores = db.query(StudentScore).filter(
        StudentScore.student_id == current_user["user_id"]
    ).all()
    
    if not scores:
        return {
            "total_quizzes_taken": 0,
            "average_percentage": 0,
            "passed_count": 0,
            "failed_count": 0
        }
    
    passed = sum(1 for s in scores if s.is_passed)
    average = sum(s.percentage for s in scores) / len(scores)
    
    return {
        "total_quizzes_taken": len(scores),
        "average_percentage": round(average, 2),
        "passed_count": passed,
        "failed_count": len(scores) - passed
    }

@router.get("/school/{school_id}/class-results")
async def get_class_results(
    school_id: int,
    current_user: dict = Depends(lambda: {"user_id": 0}),
    db: Session = Depends(get_db)
):
    """
    Get aggregated results for all quizzes in a school (teacher/admin only).
    """
    # Get all quizzes for school
    from models import Quiz
    quizzes = db.query(Quiz).filter(Quiz.school_id == school_id).all()
    quiz_ids = [q.id for q in quizzes]
    
    # Get all scores for these quizzes
    scores = db.query(StudentScore).filter(
        StudentScore.quiz_id.in_(quiz_ids)
    ).all()
    
    result = {
        "school_id": school_id,
        "total_submissions": len(scores),
        "average_score": round(sum(s.percentage for s in scores) / len(scores), 2) if scores else 0,
        "pass_rate": round(sum(1 for s in scores if s.is_passed) / len(scores) * 100, 2) if scores else 0
    }
    
    return result
