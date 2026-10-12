"""
Seed script to populate the database with sample data for testing.
Run from the backend directory: python seed_data.py
"""
import os
import sys
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, Base, engine
from app.models.models import User, Grievance, Department
from app.core.security import hash_password

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if data already exists
    existing_users = db.query(User).count()
    if existing_users > 0:
        print("✓ Database already seeded. Skipping...")
        sys.exit(0)

    # Create Departments
    print("Creating departments...")
    dept_academic = Department(
        name="Academic Affairs",
        category="academic",
        contact_email="academic@college.edu",
        sla_hours=72
    )
    dept_fees = Department(
        name="Finance",
        category="fees",
        contact_email="fees@college.edu",
        sla_hours=48
    )
    dept_hostel = Department(
        name="Hostel Services",
        category="hostel",
        contact_email="hostel@college.edu",
        sla_hours=24
    )
    
    db.add_all([dept_academic, dept_fees, dept_hostel])
    db.commit()
    print("✓ Departments created")

    # Create Users
    print("Creating users...")
    
    # Admin user
    admin = User(
        email="admin@college.edu",
        name="Admin User",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        department_id=dept_academic.id,
    )
    
    # Staff users
    staff_academic = User(
        email="academic.staff@college.edu",
        name="Dr. Sarah Johnson",
        hashed_password=get_password_hash("staff123"),
        role="staff",
        department_id=dept_academic.id,
    )
    
    staff_fees = User(
        email="fees.staff@college.edu",
        name="Mr. Rajesh Kumar",
        hashed_password=get_password_hash("staff123"),
        role="staff",
        department_id=dept_fees.id,
    )
    
    staff_hostel = User(
        email="hostel.staff@college.edu",
        name="Mrs. Priya Sharma",
        hashed_password=get_password_hash("staff123"),
        role="staff",
        department_id=dept_hostel.id,
    )
    
    # Student users
    student1 = User(
        email="student@college.edu",
        name="Arjun Singh",
        hashed_password=get_password_hash("student123"),
        role="student",
    )
    
    student2 = User(
        email="sneha.patel@college.edu",
        name="Sneha Patel",
        hashed_password=get_password_hash("student123"),
        role="student",
    )
    
    student3 = User(
        email="vikram.desai@college.edu",
        name="Vikram Desai",
        hashed_password=get_password_hash("student123"),
        role="student",
    )
    
    db.add_all([admin, staff_academic, staff_fees, staff_hostel, student1, student2, student3])
    db.commit()
    print("✓ Users created")

    # Create Grievances
    print("Creating sample grievances...")
    
    now = datetime.now()
    
    grievances_data = [
        {
            "student_id": student1.id,
            "department_id": dept_academic.id,
            "raw_text": "My final exam marks for Math have not been uploaded to the system even after 2 weeks.",
            "category": "academic",
            "priority": "high",
            "status": "in_progress",
            "created_at": now - timedelta(days=5),
        },
        {
            "student_id": student2.id,
            "department_id": dept_hostel.id,
            "raw_text": "The AC in my hostel room is not working and the walls have severe dampness.",
            "category": "hostel",
            "priority": "medium",
            "status": "in_progress",
            "created_at": now - timedelta(days=3),
        },
        {
            "student_id": student3.id,
            "department_id": dept_fees.id,
            "raw_text": "I was charged twice for my semester fee. Please refund the duplicate amount.",
            "category": "fees",
            "priority": "high",
            "status": "submitted",
            "created_at": now - timedelta(days=7),
        },
        {
            "student_id": student1.id,
            "department_id": dept_academic.id,
            "raw_text": "My assignment was graded unfairly. I believe I deserve at least 5 marks more.",
            "category": "academic",
            "priority": "medium",
            "status": "resolved",
            "created_at": now - timedelta(days=10),
        },
        {
            "student_id": student2.id,
            "department_id": dept_hostel.id,
            "raw_text": "The hostel food court is extremely dirty. Tables are not cleaned and there are insects.",
            "category": "hostel",
            "priority": "high",
            "status": "submitted",
            "created_at": now - timedelta(days=2),
        },
        {
            "student_id": student3.id,
            "department_id": dept_fees.id,
            "raw_text": "I submitted late registration but the fee waiver was not processed.",
            "category": "fees",
            "priority": "medium",
            "status": "in_progress",
            "created_at": now - timedelta(days=4),
        },
    ]

    for gdata in grievances_data:
        g = Grievance(**gdata)
        db.add(g)
    
    db.commit()
    print("✓ Sample grievances created")

    print("\n" + "="*60)
    print("DATABASE SEED COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nTest Credentials:")
    print("-" * 60)
    print("ADMIN:")
    print("  Email: admin@college.edu")
    print("  Password: admin123")
    print("\nSTAFF (Academic):")
    print("  Email: academic.staff@college.edu")
    print("  Password: staff123")
    print("\nSTAFF (Fees):")
    print("  Email: fees.staff@college.edu")
    print("  Password: staff123")
    print("\nSTAFF (Hostel):")
    print("  Email: hostel.staff@college.edu")
    print("  Password: staff123")
    print("\nSTUDENT:")
    print("  Email: student@college.edu")
    print("  Password: student123")
    print("  (Also: sneha.patel@college.edu, vikram.desai@college.edu)")
    print("-" * 60)
    print("\nFrontend: http://localhost:5173")
    print("Backend API: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("="*60)

except Exception as e:
    print(f"✗ Error seeding database: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
