#!/usr/bin/env python3
"""
Script to populate sample quizzes into the database for testing.
"""

from database import SessionLocal
from models import Quiz, Question, Answer, School

def add_sample_quizzes():
    """Add sample quizzes about Uzbek Kandakorlik art"""
    db = SessionLocal()
    
    try:
        # Get a school to attach quizzes to (use Samarkand)
        school = db.query(School).filter(School.slug == "samarkand").first()
        if not school:
            print("❌ No school found. Please run init_db.py first.")
            return
        
        # Check if quizzes already exist
        existing = db.query(Quiz).filter(Quiz.school_id == school.id).first()
        if existing:
            print("ℹ️ Quizzes already exist for this school. Skipping...")
            return
        
        print("🎓 Creating sample quizzes...")
        
        # Quiz 1: Introduction to Kandakorlik
        quiz1 = Quiz(
            school_id=school.id,
            title="Introduction to Kandakorlik",
            description="Learn the basics of Uzbek copper engraving art",
            time_limit_minutes=15,
            passing_score=70.0,
            total_questions=3,
            is_published=True
        )
        db.add(quiz1)
        db.flush()
        
        # Questions for Quiz 1
        q1 = Question(
            quiz_id=quiz1.id,
            question_text="What is Kandakorlik?",
            question_type="multiple_choice",
            order=1,
            points=1.0
        )
        db.add(q1)
        db.flush()
        
        answers_q1 = [
            Answer(question_id=q1.id, answer_text="Traditional Uzbek copper engraving art", is_correct=True, order=1, explanation="Kandakorlik is the traditional Uzbek art of engraving designs on copper."),
            Answer(question_id=q1.id, answer_text="A type of textile weaving", is_correct=False, order=2),
            Answer(question_id=q1.id, answer_text="A pottery technique", is_correct=False, order=3),
        ]
        db.add_all(answers_q1)
        
        q2 = Question(
            quiz_id=quiz1.id,
            question_text="Which regions are famous for Kandakorlik?",
            question_type="multiple_choice",
            order=2,
            points=1.0
        )
        db.add(q2)
        db.flush()
        
        answers_q2 = [
            Answer(question_id=q2.id, answer_text="Bukhara and Samarkand", is_correct=True, order=1, explanation="These cities are the primary centers of Kandakorlik tradition."),
            Answer(question_id=q2.id, answer_text="Moscow and St. Petersburg", is_correct=False, order=2),
            Answer(question_id=q2.id, answer_text="Istanbul and Cairo", is_correct=False, order=3),
        ]
        db.add_all(answers_q2)
        
        q3 = Question(
            quiz_id=quiz1.id,
            question_text="What material is primarily used in Kandakorlik?",
            question_type="multiple_choice",
            order=3,
            points=1.0
        )
        db.add(q3)
        db.flush()
        
        answers_q3 = [
            Answer(question_id=q3.id, answer_text="Copper", is_correct=True, order=1, explanation="Copper is the primary material for Kandakorlik engraving."),
            Answer(question_id=q3.id, answer_text="Silver", is_correct=False, order=2),
            Answer(question_id=q3.id, answer_text="Bronze", is_correct=False, order=3),
        ]
        db.add_all(answers_q3)
        
        # Quiz 2: Design Patterns and Techniques
        quiz2 = Quiz(
            school_id=school.id,
            title="Design Patterns and Techniques",
            description="Understand the various patterns and techniques used in Kandakorlik",
            time_limit_minutes=20,
            passing_score=70.0,
            total_questions=3,
            is_published=True
        )
        db.add(quiz2)
        db.flush()
        
        q4 = Question(
            quiz_id=quiz2.id,
            question_text="What is the 'Chekma' technique?",
            question_type="multiple_choice",
            order=1,
            points=1.0
        )
        db.add(q4)
        db.flush()
        
        answers_q4 = [
            Answer(question_id=q4.id, answer_text="A dotted background technique creating elegant patterns", is_correct=True, order=1, explanation="Chekma is a distinctive Bukhara technique using dots for background effects."),
            Answer(question_id=q4.id, answer_text="A type of metal alloy", is_correct=False, order=2),
            Answer(question_id=q4.id, answer_text="A tool used in engraving", is_correct=False, order=3),
        ]
        db.add_all(answers_q4)
        
        q5 = Question(
            quiz_id=quiz2.id,
            question_text="What characterizes Samarkand-style Kandakorlik?",
            question_type="multiple_choice",
            order=2,
            points=1.0
        )
        db.add(q5)
        db.flush()
        
        answers_q5 = [
            Answer(question_id=q5.id, answer_text="Complex geometric patterns with sophisticated shadow effects", is_correct=True, order=1, explanation="Samarkand style features intricate geometric designs and shadow work."),
            Answer(question_id=q5.id, answer_text="Simple, minimalist designs", is_correct=False, order=2),
            Answer(question_id=q5.id, answer_text="Large bold letters", is_correct=False, order=3),
        ]
        db.add_all(answers_q5)
        
        q6 = Question(
            quiz_id=quiz2.id,
            question_text="Which style uses bold large-scale botanical patterns?",
            question_type="multiple_choice",
            order=3,
            points=1.0
        )
        db.add(q6)
        db.flush()
        
        answers_q6 = [
            Answer(question_id=q6.id, answer_text="Fergana style", is_correct=True, order=1, explanation="Fergana is known for bold, large-scale botanical motifs."),
            Answer(question_id=q6.id, answer_text="Bukhara style", is_correct=False, order=2),
            Answer(question_id=q6.id, answer_text="Tashkent style", is_correct=False, order=3),
        ]
        db.add_all(answers_q6)
        
        db.commit()
        print("✅ Successfully created 2 sample quizzes with 6 questions total!")
        print("   Quiz 1: Introduction to Kandakorlik (3 questions)")
        print("   Quiz 2: Design Patterns and Techniques (3 questions)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_quizzes()
