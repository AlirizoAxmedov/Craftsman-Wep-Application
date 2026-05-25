#!/usr/bin/env python3
"""
Database initialization script for Kandakorlik platform.
Creates tables and populates with initial school data.

Usage: python init_db.py
"""

from database import SessionLocal, engine
from models import Base, School, User, UserRole, Quiz, Question, Answer
from security import hash_password
import sys

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
        
        # Create demo admin user
        print("\n👤 Creating demo admin user...")
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            admin = User(
                username="admin",
                email="admin@kandakorlik.local",
                hashed_password=hash_password("AdminPass123"),
                full_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            print("  • Admin user created")
            print("     Username: admin")
            print("     Password: AdminPass123")
        else:
            print("  • Admin user already exists")
        
        # Create demo teacher user
        print("\n👤 Creating demo teacher user...")
        teacher = db.query(User).filter(User.username == "teacher").first()
        
        if not teacher:
            teacher = User(
                username="teacher",
                email="teacher@kandakorlik.local",
                hashed_password=hash_password("TeacherPass123"),
                full_name="Instructor Ali",
                role=UserRole.TEACHER,
                is_active=True
            )
            db.add(teacher)
            print("  • Teacher user created")
            print("     Username: teacher")
            print("     Password: TeacherPass123")
        else:
            print("  • Teacher user already exists")
        
        # Create demo student user
        print("\n👤 Creating demo student user...")
        student = db.query(User).filter(User.username == "student").first()
        
        if not student:
            student = User(
                username="student",
                email="student@kandakorlik.local",
                hashed_password=hash_password("StudentPass123"),
                full_name="Zainab Ahmed",
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student)
            print("  • Student user created")
            print("     Username: student")
            print("     Password: StudentPass123")
        else:
            print("  • Student user already exists")
        
        db.commit()
        print("✓ Demo users initialized")
        
        # Seed quizzes if none exist
        if db.query(Quiz).count() == 0:
            print("\n📝 Seeding sample quizzes...")
            school = db.query(School).filter(School.slug == "samarkand").first()
            if school:
                quizzes_data = [
                    {
                        "title": "Kandakorlik asoslari",
                        "description": "O'zbek mis o'ymakorligi san'atining asosiy tushunchalari",
                        "questions": [
                            {
                                "text": "Kandakorlik nima?",
                                "answers": [
                                    ("Misga naqsh o'yish an'anaviy o'zbek san'ati", True),
                                    ("To'qimachilik turi", False),
                                    ("Kulolchilik usuli", False),
                                    ("Naqqoshlik san'ati", False),
                                ]
                            },
                            {
                                "text": "Kandakorlik uchun asosan qaysi material ishlatiladi?",
                                "answers": [
                                    ("Mis", True),
                                    ("Kumush", False),
                                    ("Bronza", False),
                                    ("Temir", False),
                                ]
                            },
                            {
                                "text": "Qaysi shaharlar kandakorlik markazi hisoblanadi?",
                                "answers": [
                                    ("Buxoro va Samarqand", True),
                                    ("Toshkent va Namangan", False),
                                    ("Andijon va Qo'qon", False),
                                    ("Termiz va Qarshi", False),
                                ]
                            },
                        ]
                    },
                    {
                        "title": "Naqsh turlari va texnikalar",
                        "description": "Kandakorlikda ishlatiladigan naqsh va texnikalar",
                        "questions": [
                            {
                                "text": "'Chekma' texnikasi nima?",
                                "answers": [
                                    ("Nuqtali fon yaratuvchi Buxoro texnikasi", True),
                                    ("Metal qotishmasi turi", False),
                                    ("O'ymakorlik asbobi", False),
                                    ("Buyumni jilolash usuli", False),
                                ]
                            },
                            {
                                "text": "Samarqand uslubidagi kandakorlik qanday xususiyatga ega?",
                                "answers": [
                                    ("Murakkab geometrik naqshlar va soya effektlari", True),
                                    ("Sodda minimalist dizayn", False),
                                    ("Yirik harflar", False),
                                    ("Rangli bo'yoqlar", False),
                                ]
                            },
                            {
                                "text": "Qaysi maktab yirik o'simlik naqshlari bilan mashhur?",
                                "answers": [
                                    ("Farg'ona maktabi", True),
                                    ("Buxoro maktabi", False),
                                    ("Toshkent maktabi", False),
                                    ("Xorazm maktabi", False),
                                ]
                            },
                        ]
                    },
                    {
                        "title": "Asboblar va jarayonlar",
                        "description": "Kandakorlikda ishlatiladigan asboblar va ish jarayonlari",
                        "questions": [
                            {
                                "text": "Mazutga yopishtirish jarayoni nima uchun kerak?",
                                "answers": [
                                    ("Buyumni mahkam ushlab turish uchun", True),
                                    ("Buyumni bo'yash uchun", False),
                                    ("Metalga rang berish uchun", False),
                                    ("Buyumni tozalash uchun", False),
                                ]
                            },
                            {
                                "text": "Sayqalash jarayoni qaysi bosqichda amalga oshiriladi?",
                                "answers": [
                                    ("Naqsh o'yilgandan keyin", True),
                                    ("Naqsh o'yilishidan oldin", False),
                                    ("Mazutga yopishtirishdan oldin", False),
                                    ("Dizayn chizilganda", False),
                                ]
                            },
                            {
                                "text": "Kopirovka (eskizni ko'chirish) nima uchun ishlatiladi?",
                                "answers": [
                                    ("Naqsh rasmini misga o'tkazish uchun", True),
                                    ("Metalga rang berish uchun", False),
                                    ("Buyumni tozalash uchun", False),
                                    ("Asboblarni keskirlash uchun", False),
                                ]
                            },
                        ]
                    },
                    {
                        "title": "Maktablar va an'analar",
                        "description": "O'zbek kandakorlik maktablari va ularning tarixi",
                        "questions": [
                            {
                                "text": "Buxoro kandakorlik maktabi qaysi davr bilan bog'liq?",
                                "answers": [
                                    ("XIX asr o'rtalari — hozirgi kun", True),
                                    ("Faqat XX asr", False),
                                    ("Qadimgi Rim davri", False),
                                    ("Sovet davri", False),
                                ]
                            },
                            {
                                "text": "Xorazm kandakorlik maktabining o'ziga xos xususiyati nima?",
                                "answers": [
                                    ("Nozik sim inlay va forsiy ta'sir", True),
                                    ("Zamonaviy minimal dizayn", False),
                                    ("Faqat geometrik shakllar", False),
                                    ("Bo'yoqli bezaklar", False),
                                ]
                            },
                            {
                                "text": "Kandakorlik qaysi turdagi san'at hisoblanadi?",
                                "answers": [
                                    ("Hunarmandchilik va bezak san'ati", True),
                                    ("Rasm chizish san'ati", False),
                                    ("Me'morchilik", False),
                                    ("Musiqa san'ati", False),
                                ]
                            },
                        ]
                    },
                ]

                for qd in quizzes_data:
                    quiz = Quiz(
                        school_id=school.id,
                        title=qd["title"],
                        description=qd["description"],
                        time_limit_minutes=20,
                        passing_score=60.0,
                        total_questions=len(qd["questions"]),
                        is_published=True,
                    )
                    db.add(quiz)
                    db.flush()
                    for i, q in enumerate(qd["questions"], 1):
                        question = Question(
                            quiz_id=quiz.id,
                            question_text=q["text"],
                            question_type="multiple_choice",
                            order=i,
                            points=1.0,
                        )
                        db.add(question)
                        db.flush()
                        for j, (ans_text, is_correct) in enumerate(q["answers"], 1):
                            db.add(Answer(
                                question_id=question.id,
                                answer_text=ans_text,
                                is_correct=is_correct,
                                order=j,
                            ))
                    print(f"  • Created quiz: {qd['title']}")

                db.commit()
                print(f"✓ {len(quizzes_data)} quizzes seeded")
            else:
                print("  ⚠ Samarkand school not found, skipping quiz seed")
        else:
            print("\n✓ Quizzes already exist, skipping seed")

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
