#!/usr/bin/env python3
"""
Database initialization script for Kandakorlik platform.
Creates tables and populates with initial school data.

Usage: python init_db.py
"""

from database import SessionLocal, engine
from models import Base, School, User, UserRole, Quiz, Question, Answer
from security import hash_password, verify_password
import json
import os
import secrets
import sys

# Placeholder quizzes seeded by earlier versions of this script, before the real
# question bank was extracted from the DOCX. Removed on sight.
LEGACY_DEMO_QUIZ_TITLES = [
    "Kandakorlik asoslari",
    "Naqsh turlari va texnikalar",
    "Asboblar va jarayonlar",
    "Maktablar va an'analar",
    "Introduction to Kandakorlik",
    "Design Patterns and Techniques",
]

def init_database():
    """Create all tables and populate initial data"""
    
    print("🔨 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")
    
    db = SessionLocal()
    
    try:
        # Initialize schools data
        schools_data = [
            {
                "name": "Buxoro",
                "english_name": "Bukhara",
                "slug": "bukhara",
                "historical_period": "Mid-19th century - present",
                "distinctive_style": "Elegant and simple designs with 'Chekma' dotted background technique"
            },
            {
                "name": "Samarqand",
                "english_name": "Samarkand",
                "slug": "samarkand",
                "historical_period": "14th century - present",
                "distinctive_style": "Complex geometric patterns with sophisticated 'Ghufran' shadow effects"
            },
            {
                "name": "Farg'ona",
                "english_name": "Fergana",
                "slug": "fergana",
                "historical_period": "16th century - present",
                "distinctive_style": "Bold large-scale patterns with dense botanical motifs"
            },
            {
                "name": "Xorazm",
                "english_name": "Khorezm",
                "slug": "khorezm",
                "historical_period": "Medieval - present",
                "distinctive_style": "Ornate designs with fine wire inlay and Persian influences"
            },
            {
                "name": "Toshkent",
                "english_name": "Tashkent",
                "slug": "tashkent",
                "historical_period": "Modern era",
                "distinctive_style": "Blend of traditional and contemporary techniques"
            },
            {
                "name": "Qarshi",
                "english_name": "Karshi",
                "slug": "karshi",
                "historical_period": "Medieval - present",
                "distinctive_style": "Practical designs combining beauty with functionality"
            }
        ]
        
        print("\n📚 Adding Uzbek engraving schools...")
        for school_data in schools_data:
            # Check if school already exists
            existing = db.query(School).filter(School.slug == school_data["slug"]).first()
            if existing:
                print(f"  • {school_data['english_name']} (already exists)")
                continue
            
            school = School(**school_data)
            db.add(school)
            print(f"  • Added {school_data['english_name']}")
        
        db.commit()
        print("✓ Schools data initialized")
        
        # Seed the built-in accounts. Passwords come from the environment —
        # never from this file, which is public. Setting the variable to a new
        # value rotates that account's password on the next deploy.
        print("\n👤 Seeding built-in accounts...")
        seeded_accounts = [
            ("ADMIN_PASSWORD", "admin", "admin@kandakorlik.local", "Administrator", UserRole.ADMIN),
            ("TEACHER_PASSWORD", "teacher", "teacher@kandakorlik.local", "Instructor Ali", UserRole.TEACHER),
            ("STUDENT_PASSWORD", "student", "student@kandakorlik.local", "Zainab Ahmed", UserRole.STUDENT),
        ]

        for env_var, username, email, full_name, role in seeded_accounts:
            desired = os.environ.get(env_var)
            user = db.query(User).filter(User.username == username).first()

            if not user:
                # No password supplied for a brand-new account: generate one
                # rather than shipping a known default. It is printed once here
                # and recoverable only from this deploy log.
                generated = desired is None
                password = desired or secrets.token_urlsafe(18)
                db.add(User(
                    username=username,
                    email=email,
                    hashed_password=hash_password(password),
                    full_name=full_name,
                    role=role,
                    is_active=True,
                ))
                print(f"  • Created {username} ({role.value})")
                if generated:
                    print(f"     Generated password: {password}")
                    print(f"     Set {env_var} to choose your own.")
                else:
                    print(f"     Password taken from {env_var}")
            elif desired and not verify_password(desired, user.hashed_password):
                user.hashed_password = hash_password(desired)
                print(f"  • Rotated {username} password from {env_var}")
            else:
                print(f"  • {username} already exists")

        db.commit()
        print("✓ Built-in accounts initialized")
        
        # Seed the real quizzes from quiz_seed_data.json (generated by
        # extract_quizzes.py from 'ТЕСТЫ по Чеканке.docx').
        print("\n📝 Seeding quizzes...")
        seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_seed_data.json")
        if not os.path.exists(seed_path):
            print(f"  ⚠ {seed_path} not found, skipping quiz seed")
        else:
            with open(seed_path, encoding="utf-8") as f:
                quizzes_data = json.load(f)

            school = db.query(School).filter(School.slug == "bukhara").first()
            if not school:
                print("  ⚠ Bukhara school not found, skipping quiz seed")
            else:
                # Drop the old 3-question demo quizzes that shipped before the
                # real question bank existed. The question-count check keeps this
                # from ever touching a real quiz that reuses one of these titles.
                for quiz in db.query(Quiz).filter(Quiz.title.in_(LEGACY_DEMO_QUIZ_TITLES)).all():
                    if len(quiz.questions) <= 3:
                        print(f"  • Removing demo quiz: {quiz.title}")
                        db.delete(quiz)
                db.flush()

                for qd in quizzes_data:
                    expected = len(qd["questions"])
                    existing = db.query(Quiz).filter(
                        Quiz.school_id == school.id,
                        Quiz.title == qd["title"],
                    ).first()

                    # Already correct — leave it alone so student scores survive
                    # the redeploy (this runs as a pre-deploy step every time).
                    if existing and len(existing.questions) == expected:
                        print(f"  • Up to date: {qd['title']} ({expected} questions)")
                        continue

                    if existing:
                        print(f"  • Replacing: {qd['title']} "
                              f"({len(existing.questions)} → {expected} questions)")
                        db.delete(existing)
                        db.flush()

                    quiz = Quiz(
                        school_id=school.id,
                        title=qd["title"],
                        description=qd["description"],
                        time_limit_minutes=qd["time_limit_minutes"],
                        passing_score=qd["passing_score"],
                        total_questions=expected,
                        is_published=True,
                    )
                    db.add(quiz)
                    db.flush()
                    for q in qd["questions"]:
                        question = Question(
                            quiz_id=quiz.id,
                            question_text=q["question_text"],
                            question_type=q["question_type"],
                            order=q["order"],
                            points=q["points"],
                        )
                        db.add(question)
                        db.flush()
                        for a in q["answers"]:
                            db.add(Answer(
                                question_id=question.id,
                                answer_text=a["answer_text"],
                                is_correct=a["is_correct"],
                                order=a["order"],
                            ))
                    print(f"  • Created quiz: {qd['title']} ({expected} questions)")

                db.commit()
                total = sum(len(qd["questions"]) for qd in quizzes_data)
                print(f"✓ {len(quizzes_data)} quizzes / {total} questions seeded")

        print("\n" + "="*50)
        print("✓ Database initialization complete!")
        print("="*50)
        print("\n📝 Next steps:")
        print("1. Start the server: python main.py")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Login with demo credentials above")
        print("4. Create quizzes and invite students")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}", file=sys.stderr)
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
