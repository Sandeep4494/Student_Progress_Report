"""
Seed script to populate database with sample data
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from passlib.context import CryptContext
from db.database import SessionLocal, init_db
from db.models import User, Student, AttendanceRecord, AcademicScore, EngagementLog

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def seed_database():
    """Seed the database with sample data"""
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - comment out if you want to keep existing data)
        db.query(EngagementLog).delete()
        db.query(AcademicScore).delete()
        db.query(AttendanceRecord).delete()
        db.query(Student).delete()
        db.query(User).delete()
        db.commit()
        
        # Create parent users
        parents = [
            User(
                username="parent1",
                email="parent1@example.com",
                hashed_password=hash_password("password123"),
                full_name="John Smith"
            ),
            User(
                username="parent2",
                email="parent2@example.com",
                hashed_password=hash_password("password123"),
                full_name="Jane Doe"
            ),
        ]
        
        for parent in parents:
            db.add(parent)
        db.commit()
        
        # Create students
        students_data = [
            {
                "student_id": "STU001",
                "full_name": "Alice Smith",
                "email": "alice@university.edu",
                "parent_id": parents[0].id
            },
            {
                "student_id": "STU002",
                "full_name": "Bob Smith",
                "email": "bob@university.edu",
                "parent_id": parents[0].id
            },
            {
                "student_id": "STU003",
                "full_name": "Charlie Doe",
                "email": "charlie@university.edu",
                "parent_id": parents[1].id
            },
        ]
        
        students = []
        for student_data in students_data:
            student = Student(**student_data)
            db.add(student)
            students.append(student)
        db.commit()
        
        # Generate attendance records (last 30 days)
        subjects = ["Mathematics", "Science", "English", "History", "Computer Science"]
        statuses = ["present", "absent", "late", "excused"]
        status_weights = [0.75, 0.15, 0.05, 0.05]  # 75% present, 15% absent, etc.
        
        for student in students:
            for day in range(30):
                date = datetime.now() - timedelta(days=30 - day)
                # Skip weekends (optional)
                if date.weekday() < 5:  # Monday to Friday
                    for subject in subjects:
                        status = random.choices(statuses, weights=status_weights)[0]
                        attendance = AttendanceRecord(
                            student_id=student.id,
                            date=date.replace(hour=9 + random.randint(0, 6)),
                            status=status,
                            class_name=subject
                        )
                        db.add(attendance)
        
        db.commit()
        
        # Generate academic scores
        subjects_academic = ["Mathematics", "Science", "English", "History", "Computer Science"]
        assessment_types = ["exam", "quiz", "assignment", "project"]
        
        for student in students:
            for subject in subjects_academic:
                # Generate scores over the last 3 months
                for month in range(3):
                    base_date = datetime.now() - timedelta(days=90 - (month * 30))
                    
                    # Exams
                    for exam_num in range(2):
                        score = random.uniform(60, 100)
                        max_score = 100
                        academic_score = AcademicScore(
                            student_id=student.id,
                            subject=subject,
                            assessment_type="exam",
                            score=score,
                            max_score=max_score,
                            percentage=(score / max_score) * 100,
                            date=base_date + timedelta(days=exam_num * 15)
                        )
                        db.add(academic_score)
                    
                    # Quizzes
                    for quiz_num in range(4):
                        score = random.uniform(70, 95)
                        max_score = 20
                        academic_score = AcademicScore(
                            student_id=student.id,
                            subject=subject,
                            assessment_type="quiz",
                            score=score,
                            max_score=max_score,
                            percentage=(score / max_score) * 100,
                            date=base_date + timedelta(days=quiz_num * 7)
                        )
                        db.add(academic_score)
                    
                    # Assignments
                    for assign_num in range(5):
                        score = random.uniform(75, 100)
                        max_score = 100
                        academic_score = AcademicScore(
                            student_id=student.id,
                            subject=subject,
                            assessment_type="assignment",
                            score=score,
                            max_score=max_score,
                            percentage=(score / max_score) * 100,
                            date=base_date + timedelta(days=assign_num * 6)
                        )
                        db.add(academic_score)
        
        db.commit()
        
        # Generate engagement logs
        activity_types = ["login", "assignment_submitted", "video_watched", "quiz_taken", "forum_post"]
        
        for student in students:
            # Generate engagement over last 30 days
            for day in range(30):
                date = datetime.now() - timedelta(days=30 - day)
                
                # Daily login (80% chance)
                if random.random() < 0.8:
                    login_time = date.replace(hour=random.randint(8, 22))
                    engagement = EngagementLog(
                        student_id=student.id,
                        activity_type="login",
                        activity_details=f"LMS login at {login_time.strftime('%H:%M')}",
                        timestamp=login_time
                    )
                    db.add(engagement)
                
                # Random activities throughout the day
                num_activities = random.randint(0, 5)
                for _ in range(num_activities):
                    activity_type = random.choice(activity_types)
                    activity_time = date.replace(hour=random.randint(8, 22))
                    engagement = EngagementLog(
                        student_id=student.id,
                        activity_type=activity_type,
                        activity_details=f"{activity_type} activity",
                        timestamp=activity_time
                    )
                    db.add(engagement)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - Created {len(parents)} parents")
        print(f"   - Created {len(students)} students")
        print(f"   - Generated attendance records")
        print(f"   - Generated academic scores")
        print(f"   - Generated engagement logs")
        print("\n📝 Test credentials:")
        print("   Username: parent1")
        print("   Password: password123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()


