"""
Seeds the database with departments + demo accounts so you can log in
and test immediately. Run with:
  python -m app.db.seed
"""
from app.db.session import SessionLocal, Base, engine
from app.models.models import Department, User, UserRole, GrievanceCategory
from app.core.security import hash_password

DEPARTMENTS = [
    {"name": "Academic Affairs", "category": GrievanceCategory.academic, "sla_hours": 72},
    {"name": "Accounts & Fees Office", "category": GrievanceCategory.fees, "sla_hours": 48},
    {"name": "Hostel Administration", "category": GrievanceCategory.hostel, "sla_hours": 96},
    {"name": "Examination Cell (Attendance)", "category": GrievanceCategory.attendance, "sla_hours": 72},
    {"name": "Records & Certificates Office", "category": GrievanceCategory.certificates, "sla_hours": 120},
    {"name": "Facilities & Infrastructure", "category": GrievanceCategory.infrastructure, "sla_hours": 48},
    {"name": "General Administration", "category": GrievanceCategory.other, "sla_hours": 72},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        dept_objs = {}
        for d in DEPARTMENTS:
            existing = db.query(Department).filter(Department.category == d["category"]).first()
            if existing:
                dept_objs[d["category"]] = existing
                continue
            dept = Department(**d)
            db.add(dept)
            db.flush()
            dept_objs[d["category"]] = dept
        db.commit()
        print(f"Seeded {len(DEPARTMENTS)} departments.")

        demo_accounts = [
            {"name": "Admin User", "email": "admin@college.edu", "password": "admin123", "role": UserRole.admin},
            {"name": "Fees Officer", "email": "fees.staff@college.edu", "password": "staff123",
             "role": UserRole.staff, "department": GrievanceCategory.fees},
            {"name": "Hostel Warden", "email": "hostel.staff@college.edu", "password": "staff123",
             "role": UserRole.staff, "department": GrievanceCategory.hostel},
            {"name": "Demo Student", "email": "student@college.edu", "password": "student123", "role": UserRole.student},
        ]

        for acc in demo_accounts:
            existing = db.query(User).filter(User.email == acc["email"]).first()
            if existing:
                continue
            dept_id = dept_objs[acc["department"]].id if "department" in acc else None
            user = User(
                name=acc["name"], email=acc["email"],
                hashed_password=hash_password(acc["password"]),
                role=acc["role"], department_id=dept_id,
            )
            db.add(user)
        db.commit()
        print("Seeded demo accounts:")
        for acc in demo_accounts:
            print(f"  {acc['role'].value:8s} | {acc['email']:25s} | password: {acc['password']}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
