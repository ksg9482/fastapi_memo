from passlib.context import CryptContext
from requests import Session

from database import AsyncSessionLocal

# db에 의존성 넣어주는 기능 모음이라 dependencies?
# 공통기능?
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_db():
    # get_db 호출하면 비동기로 호출된 세션을 통해 DB접근 진행
    async with AsyncSessionLocal() as session:
        # 먼저 yield를 통해 세션 제어를 다시 돌려주고, 커밋함
        yield session
        await session.commit()