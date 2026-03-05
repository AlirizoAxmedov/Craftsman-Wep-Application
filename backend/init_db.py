#!/usr/bin/env python3
"""
Database initialization script for Kandakorlik platform.
Creates tables and populates with initial school data.

Usage: python init_db.py
"""

from database import SessionLocal, engine
from models import Base, School, User, UserRole
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
