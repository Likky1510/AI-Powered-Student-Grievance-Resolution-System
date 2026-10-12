from app.db.session import SessionLocal
from app.models.models import User
from app.core.security import create_access_token

if __name__ == '__main__':
    db = SessionLocal()
    user = db.query(User).filter(User.email == 'student@college.edu').first()
    if not user:
        print('NO_USER')
    else:
        token = create_access_token({'sub': user.id, 'role': user.role.value})
        print(token)
        print('USER_ID:', user.id)
    db.close()
