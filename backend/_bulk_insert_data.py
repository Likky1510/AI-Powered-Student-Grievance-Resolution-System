"""
Bulk test data insertion script.
Inserts sample grievances directly into the database for testing.
Useful for load testing and evaluating system behavior with real data.
"""
import sys
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.models.models import User, Grievance, Department, GrievanceCategory, GrievancePriority, GrievanceStatus
from datetime import datetime, timedelta

# Sample test data by category
GRIEVANCES_BY_CATEGORY = {
    'academic': [
        "My exam marks are not yet published in the portal",
        "I submitted my assignment on time but it's marked as late",
        "The professor is not responding to my attendance appeal",
        "I need a syllabus clarification for the upcoming exam",
        "My lab practical marks are not updated in the system"
    ],
    'fees': [
        "I was charged double for the hostel fee this semester",
        "My scholarship has not been disbursed yet",
        "There's a discrepancy in my fee receipt",
        "I need a refund for the dropped course",
        "Late fee was incorrectly charged to my account"
    ],
    'hostel': [
        "The air conditioning in my hostel room is not working",
        "The WiFi connectivity in the hostel is very poor",
        "There are frequent power outages in the hostel building",
        "The mess food quality has deteriorated significantly",
        "Water supply is intermittent in hostel block C"
    ],
    'attendance': [
        "My attendance percentage is shown incorrectly",
        "I cannot apply for attendance condonation in the system",
        "The system shows absences I did not have",
        "My legitimate leave is not being counted",
        "Attendance update from the faculty is pending"
    ],
    'certificates': [
        "I need an urgent bonafide certificate",
        "My transcript request is pending for a month",
        "The migration certificate has not been issued",
        "I need a character certificate from the college",
        "Duplicate certificate of my degree is taking too long"
    ],
    'infrastructure': [
        "The WiFi network in the library is not stable",
        "Computer lab machines are not functioning properly",
        "The classroom projector has not been fixed",
        "Elevator in the academic building is broken",
        "Washroom facilities need urgent maintenance"
    ]
}

def insert_bulk_data():
    """Insert sample grievances for testing."""
    db = SessionLocal()
    
    try:
        # Get students and departments
        students = db.query(User).filter(User.role == 'student').all()
        departments = db.query(Department).all()
        
        if not students:
            print("❌ No student accounts found. Please seed users first.")
            return
        
        if not departments:
            print("❌ No departments found. Please seed departments first.")
            return
        
        print(f"📦 Starting bulk insertion...")
        print(f"   Students available: {len(students)}")
        print(f"   Departments available: {len(departments)}")
        
        grievance_count = 0
        now = datetime.now()
        
        # Insert grievances by category
        for category_name, complaint_texts in GRIEVANCES_BY_CATEGORY.items():
            # Find department for this category
            dept = db.query(Department).filter(
                Department.category == GrievanceCategory[category_name]
            ).first()
            
            if not dept:
                print(f"⚠️  No department for category: {category_name}")
                continue
            
            print(f"\n📝 Inserting {len(complaint_texts)} {category_name} grievances...")
            
            for idx, complaint_text in enumerate(complaint_texts):
                # Cycle through students
                student = students[idx % len(students)]
                
                # Vary the status and timestamps for realism
                statuses = [
                    GrievanceStatus.submitted,
                    GrievanceStatus.categorized,
                    GrievanceStatus.assigned,
                    GrievanceStatus.in_progress
                ]
                status = statuses[idx % len(statuses)]
                
                # Create grievance with realistic timestamps
                created_days_ago = 1 + (idx % 7)  # 1-7 days old
                created_at = now - timedelta(days=created_days_ago)
                
                grievance = Grievance(
                    student_id=student.id,
                    department_id=dept.id,
                    raw_text=complaint_text,
                    category=GrievanceCategory[category_name],
                    priority=GrievancePriority.medium if idx % 3 == 0 else GrievancePriority.low,
                    status=status,
                    created_at=created_at,
                    assigned_at=created_at + timedelta(hours=1) if status != GrievanceStatus.submitted else None
                )
                
                db.add(grievance)
                grievance_count += 1
        
        db.commit()
        
        print(f"\n✅ Successfully inserted {grievance_count} test grievances!")
        print(f"\n📊 Test data summary:")
        print(f"   - {grievance_count} total grievances created")
        print(f"   - {len(GRIEVANCES_BY_CATEGORY)} categories covered")
        print(f"   - {len(students)} student accounts utilized")
        
        # Show inserted counts by category
        for category in GRIEVANCES_BY_CATEGORY.keys():
            count = db.query(Grievance).filter(Grievance.category == GrievanceCategory[category]).count()
            print(f"   - {category}: {count} grievances")
        
        print(f"\n🔍 You can now test with this data:")
        print(f"   - Frontend: http://localhost:5173")
        print(f"   - API Docs: http://127.0.0.1:8000/docs")
        
    except Exception as e:
        print(f"❌ Error during bulk insertion: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    insert_bulk_data()
