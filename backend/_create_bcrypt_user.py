from app.db.session import SessionLocal
from app.models.models import User
from app.core.security import hash_password

db = SessionLocal()
email = 'api.test@example.com'
user = db.query(User).filter(User.email == email).first()
if user:
    print('EXISTS', user.id)
else:
    u = User(name='API Test', email=email, hashed_password=hash_password('testpass'), role='student')
    db.add(u)
    db.commit()
    db.refresh(u)
    print('CREATED', u.id)

db.close()
