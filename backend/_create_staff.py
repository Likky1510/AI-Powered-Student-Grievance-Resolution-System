from app.db.session import SessionLocal
from app.models.models import User, UserRole
from app.core.security import hash_password

db = SessionLocal()

email = 'fees.staff@example.com'
user = db.query(User).filter(User.email == email).first()
if user:
    print(f'EXISTS: {user.id}')
else:
    # Find a fees department first
    from app.models.models import Department, GrievanceCategory
    dept = db.query(Department).filter(Department.category == GrievanceCategory.fees).first()
    if not dept:
        print('NO FEES DEPT')
    else:
        u = User(
            name='Fees Staff',
            email=email,
            hashed_password=hash_password('staffpass'),
            role='staff',
            department_id=dept.id
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        print(f'CREATED STAFF: {u.id}, dept={dept.id}')

db.close()
