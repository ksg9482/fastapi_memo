from passlib.context import CryptContext
from requests import Session

from database import SessionLocal

# db에 의존성 넣어주는 기능 모음이라 dependencies?
# 공통기능?
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    db = SessionLocal() # db 바인드. 같은 db 바인딩을 유지하기 위함
    try:
        yield db # 바인딩 된 db를 제공하고 다 끝나면 db 연결 종료.
    finally:
        db.close()