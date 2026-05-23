from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from database import get_db
from models import StudentScore, Quiz, User, UserRole
from schemas import StudentScoreResponse, StudentScoreDetail, TokenData
from security import decode_token
from typing import List

router = APIRouter()


async def get_current_user(request: Request) -> TokenData:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentifikatsiya talab etiladi")
    token = auth_header.replace("Bearer ", "")
    return decode_token(token)


@router.get("/my-scores", response_model=List[StudentScoreResponse])
async def get_my_scores(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scores = db.query(StudentScore).filter(
        StudentScore.student_id == current_user.user_id
    ).order_by(StudentScore.submitted_at.desc()).all()
    return scores


@router.get("/my-scores/{quiz_id}", response_model=StudentScoreDetail)
async def get_my_quiz_score(
    quiz_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    score = db.query(StudentScore).filter(
        (StudentScore.student_id == current_user.user_id) &
        (StudentScore.quiz_id == quiz_id)
    ).first()

    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Natija topilmadi")

    return score


@router.get("/leaderboard")
async def get_leaderboard(
    quiz_id: int = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(StudentScore).order_by(StudentScore.percentage.desc())
    if quiz_id:
        query = query.filter(StudentScore.quiz_id == quiz_id)
    top_scores = query.limit(limit).all()

    return [
        {
            "rank": idx,
            "percentage": s.percentage,
            "score": s.score,
            "max_score": s.max_score,
            "is_passed": s.is_passed,
            "submitted_at": s.submitted_at,
        }
        for idx, s in enumerate(top_scores, 1)
    ]


@router.get("/student/{student_id}/scores", response_model=List[StudentScoreResponse])
async def get_student_scores(
    student_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user or (user.role == UserRole.STUDENT and current_user.user_id != student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")

    scores = db.query(StudentScore).filter(
        StudentScore.student_id == student_id
    ).order_by(StudentScore.submitted_at.desc()).all()
    return scores


@router.get("/stats/summary")
async def get_stats_summary(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scores = db.query(StudentScore).filter(
        StudentScore.student_id == current_user.user_id
    ).all()

    if not scores:
        return {"total_quizzes_taken": 0, "average_percentage": 0, "passed_count": 0, "failed_count": 0}

    passed = sum(1 for s in scores if s.is_passed)
    average = sum(s.percentage for s in scores) / len(scores)
    return {
        "total_quizzes_taken": len(scores),
        "average_percentage": round(average, 2),
        "passed_count": passed,
        "failed_count": len(scores) - passed,
    }
