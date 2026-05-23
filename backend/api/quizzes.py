from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from database import get_db
from models import Quiz, Question, Answer, StudentScore, User, School, UserRole
from schemas import QuizCreate, QuestionCreate, QuizResponse, QuizDetail, QuizDetailForStudent, StudentQuizSubmission, StudentScoreResponse, TokenData
from security import decode_token
from typing import List

router = APIRouter()


async def get_current_user(request: Request) -> TokenData:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentifikatsiya talab etiladi")
    token = auth_header.replace("Bearer ", "")
    return decode_token(token)


async def require_teacher_or_admin(request: Request, db: Session = Depends(get_db)) -> TokenData:
    token_data = await get_current_user(request)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user or user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="O'qituvchi yoki administrator huquqi talab etiladi")
    return token_data


@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: TokenData = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    school = db.query(School).filter(School.id == quiz_data.school_id).first()
    if not school:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Maktab topilmadi: {quiz_data.school_id}")

    new_quiz = Quiz(
        school_id=quiz_data.school_id,
        title=quiz_data.title,
        description=quiz_data.description,
        time_limit_minutes=quiz_data.time_limit_minutes,
        passing_score=quiz_data.passing_score,
        total_questions=len(quiz_data.questions)
    )
    db.add(new_quiz)
    db.flush()

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
    query = db.query(Quiz)
    if school_id:
        query = query.filter(Quiz.school_id == school_id)
    if published_only:
        query = query.filter(Quiz.is_published == True)
    return query.all()


@router.get("/{quiz_id}", response_model=QuizDetail)
async def get_quiz_detail(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")
    if not quiz.is_published:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu test hali nashr etilmagan")
    return quiz


@router.get("/{quiz_id}/for-student", response_model=QuizDetail)
async def get_quiz_for_student(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")
    if not quiz.is_published:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu test hali nashr etilmagan")
    return quiz


@router.post("/{quiz_id}/submit", response_model=StudentScoreResponse)
async def submit_quiz(
    quiz_id: int,
    submission: StudentQuizSubmission,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")

    if submission.quiz_id != quiz_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test ID mos kelmadi")

    previous_score = db.query(StudentScore).filter(
        (StudentScore.student_id == current_user.user_id) &
        (StudentScore.quiz_id == quiz_id)
    ).first()

    if previous_score:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Siz bu testni allaqachon topshirgansiz")

    score = 0
    max_score = 0
    answers_data = {}

    for answer in submission.answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if not question:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Savol topilmadi: {answer.question_id}")

        max_score += question.points

        if answer.answer_id:
            correct_answer = db.query(Answer).filter(
                (Answer.id == answer.answer_id) &
                (Answer.question_id == answer.question_id)
            ).first()

            if not correct_answer:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Savol {answer.question_id} uchun noto'g'ri javob")

            if correct_answer.is_correct:
                score += question.points

            answers_data[str(answer.question_id)] = {
                "selected_answer_id": answer.answer_id,
                "is_correct": correct_answer.is_correct
            }

    percentage = (score / max_score * 100) if max_score > 0 else 0
    is_passed = percentage >= quiz.passing_score

    student_score = StudentScore(
        student_id=current_user.user_id,
        quiz_id=quiz_id,
        score=score,
        max_score=max_score,
        percentage=percentage,
        is_passed=is_passed,
        time_taken_seconds=submission.time_taken_seconds,
        answers_json=answers_data
    )

    try:
        db.add(student_score)
        db.commit()
        db.refresh(student_score)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Natijani saqlashda xato yuz berdi")
    return student_score


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizCreate,
    current_user: TokenData = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")

    quiz.title = quiz_data.title
    quiz.description = quiz_data.description
    quiz.time_limit_minutes = quiz_data.time_limit_minutes
    quiz.passing_score = quiz_data.passing_score

    db.commit()
    db.refresh(quiz)
    return quiz


@router.patch("/{quiz_id}/publish")
async def publish_quiz(
    quiz_id: int,
    current_user: TokenData = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")
    quiz.is_published = True
    db.commit()
    return {"status": "published", "quiz_id": quiz.id}


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    current_user: TokenData = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")
    db.delete(quiz)
    db.commit()


@router.get("/{quiz_id}/teacher-view", response_model=QuizDetailForStudent)
async def get_quiz_teacher_view(
    quiz_id: int,
    current_user: TokenData = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Returns quiz with correct answers visible — for teacher/admin only."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")
    return quiz


@router.post("/{quiz_id}/questions", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def add_question_to_quiz(
    quiz_id: int,
    question_data: QuestionCreate,
    current_user: TokenData = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Add a new question (with answers) to an existing quiz."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")

    new_order = len(quiz.questions) + 1
    new_question = Question(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        order=new_order,
        points=question_data.points
    )
    db.add(new_question)
    db.flush()

    for ans_idx, answer_data in enumerate(question_data.answers):
        new_answer = Answer(
            question_id=new_question.id,
            answer_text=answer_data.answer_text,
            is_correct=answer_data.is_correct,
            order=ans_idx + 1,
            explanation=answer_data.explanation
        )
        db.add(new_answer)

    quiz.total_questions = new_order
    db.commit()
    db.refresh(quiz)
    return quiz


@router.patch("/{quiz_id}/unpublish")
async def unpublish_quiz(
    quiz_id: int,
    current_user: TokenData = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test topilmadi")
    quiz.is_published = False
    db.commit()
    return {"status": "unpublished", "quiz_id": quiz.id}
