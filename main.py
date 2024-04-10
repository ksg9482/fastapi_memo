from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session #DB 접속
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String #DB 테이블 정의
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional


app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "mysql+pymysql://ksg:ksg@localhost/fastapi_memo"
engine = create_engine(DATABASE_URL) # DB 접속
Base = declarative_base() # 베이스 선언. sqlalchemy orm을 이용하기 위한 root 상속

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
    db = Session(bind=engine) # db 바인드
    try:
        yield db # 바인딩 된 db를 제공하고 다 끝나면 db 연결 종료.
    finally:
        db.close()

Base.metadata.create_all(bind=engine) # 자동으로 테이블 생성

# 메모 생성
@app.post('/memos/')
async def create_memo(memo:MemoCreate, db:Session=Depends(get_db)): # Depends -> 의존성 주입
    new_memo = Memo(title=memo.title, content=memo.content)
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
async def create_memo(memo_id:int, memo:MemoUpdate, db:Session=Depends(get_db)):
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

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {
        "request": request #TemplateResponse하려면 request: Request를 기본적으로 받음. 
        })

@app.get('/about')
async def about():
    return {'message':'이것은 마이 메모 앱의 소개 페이지 입니다.'}
