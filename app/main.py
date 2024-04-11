from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session #DB 접속
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String #DB 테이블 정의
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware #세션 관리

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

app = FastAPI()
session_secret = '1234567890'
app.add_middleware(SessionMiddleware, secret_key=session_secret) # 세션 미들웨어 삽입
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "mysql+pymysql://ksg:ksg@localhost/fastapi_memo"
engine = create_engine(DATABASE_URL) # DB 접속
Base = declarative_base() # 베이스 선언. sqlalchemy orm을 이용하기 위한 root 상속

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200))
    hasd_password = Column(String(512))

class UserCreate(BaseModel):
    username: str
    email: str
    password: str # 해시 전 패스워드

class UserLogin(BaseModel):
    username: str
    password: str

class Memo(Base):
    __tablename__ = 'memo'
    id = Column(Integer, primary_key=True, index=True) # primary_key 선언하면 자동으로 Index 되지만 관례상
    title = Column(String(100))
    content = Column(String(1000))

class MemoCreate(BaseModel): # memo create dto
    title: str
    content: str

class MemoUpdate(BaseModel): # memo update dto
    title: Optional[str] = None #선택형. 기본값 설정
    content: Optional[str] = None

def get_db():
    db = Session(bind=engine) # db 바인드. 같은 db 바인딩을 유지하기 위함
    try:
        yield db # 바인딩 된 db를 제공하고 다 끝나면 db 연결 종료.
    finally:
        db.close()

Base.metadata.create_all(bind=engine) # 자동으로 테이블 생성

# 회원가입
@app.post('/signup')
async def signup(signup_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(signup_data.password)
    new_user = User(username=signup_data.username, email=signup_data.email, hasd_password=hashed_passwor )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Account created successfully", "user_id": new_user.id}

# 로그인
@app.post('/login')
async def signup(request: Request, signin_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == signin_data.username).first()
    if user and verify_password(signin_data.password, user.hasd_password):
        request.session['username'] = user.username # 세션에 유저정보를 저장해서 세션을 통해 유저정보 관리
        return {"message": "Logged in successfully"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials") # 로그인 실패. 401:인증 오류

# 로그아웃
@app.post('/logout')
async def logout(request: Request):
    request.session.pop("username", None) # 세션에서 삽입한 username 제거
    return {"message": "Logout successfully"}

"""
로그인 하면 쿠키값(세션키) 저장됨. 
로그아웃 하면 전송된 쿠키값으로 세션 제거.
"""

# 메모 생성
@app.post('/memos/')
async def create_memo(memo:MemoCreate, db:Session=Depends(get_db)): # Depends -> 의존성 주입
    new_memo = Memo(title=memo.title, content=memo.content)

    # 엔티티를 직접 다루는 것이 아니라, 엔티티를 db 엔진 (db 세션)에 넣어서 db 엔진을 조작해야 함.
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo) # DB에 저장된 값을 읽으면 입력하지 않은 id도 반환 받을 수 있음
    return ({"id": new_memo.id, "title": new_memo.title, "content": new_memo.content})

# 메모 조회
@app.get('/memos/')
async def list_memos(db:Session=Depends(get_db)):
    memos = db.query(Memo).all() # 모든 memo 다 가져오기
    return [{"id": memo.id, "title": memo.title, "content": memo.content} for memo in memos] #리스트 컴프리헨션으로 순회해서 리스트 추가

#메모 수정
@app.put('/memos/{memo_id}')
async def update_memo(memo_id:int, memo:MemoUpdate, db:Session=Depends(get_db)):
    db_memo = db.query(Memo).filter(Memo.id == memo_id).first() # 메모id가 같은 row만 필터링하고 그중 1개만 반환. findOne.
    #애초에 메모 검색 안되면 에러임
    if db_memo in None:
        return ({"error": "Memo not found"})
    
    if memo.title is not None:
        db_memo.title = memo.title

    if memo.content is not None:
        db_memo.content = memo.content

    db.commit() #변경된 레코드를 바로 커밋
    db.refresh(db_memo)

    return ({"id": db_memo.id, "title": db_memo.title, "content": db_memo.content})

# 메모 삭제
@app.delete('/memos/{memo_id}')
async def delete_memo(memo_id:int, db:Session=Depends(get_db)): # Depends -> 의존성 주입
    db_memo = db.query(Memo).filter(Memo.id == memo_id).first() # 메모id가 같은 row만 필터링하고 그중 1개만 반환. findOne.
    if db_memo in None:
        return ({"error": "Memo not found"})
    
    db.delete(db_memo)
    db.commit()
    
    return ({"mesage": "Memo deleted"})


@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {
        "request": request #TemplateResponse하려면 request: Request를 기본적으로 받음. 
        })

@app.get('/about')
async def about():
    return {'message':'이것은 마이 메모 앱의 소개 페이지 입니다.'}
