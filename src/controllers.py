
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session #DB 접속
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from dependencies import get_db, get_password_hash, verify_password
from models import Memo, User
from schemas import MemoCreate, MemoUpdate, UserCreate, UserLogin


router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 회원가입
@router.post('/signup')
# AsyncSession 비동기 세션, get_db에서 AsyncSession을 가져옴
async def signup(signup_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 비동기로 하면 excute로 함. await안쓰면 Coroutine 뜸. Promise인가?
    result = await db.execute(select(User).where(User.username == signup_data.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail='이미 가입된 사용자명입니다.')
    
    hashed_password = get_password_hash(signup_data.password)
    new_user = User(username=signup_data.username, email=signup_data.email, hasd_password=hashed_password )
    db.add(new_user)

    try:
        await db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='회원가입이 실패했습니다. 기입한 내용을 확인해보세요')
    await db.refresh(new_user)
    return {"message": "회원가입이 성공했습니다."}

# 로그인
@router.post('/login')
async def signup(request: Request, signin_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == signin_data.username))
    user = result.scalars().first()
    if user and verify_password(signin_data.password, user.hasd_password):
        request.session['username'] = user.username # 세션에 유저정보를 저장해서 세션을 통해 유저정보 관리
        return {"message": "로그인이 성공했습니다."}
    else:
        raise HTTPException(status_code=401, detail="로그인이 실패했습니다.") # 로그인 실패. 401:인증 오류

# 로그아웃
@router.post('/logout')
async def logout(request: Request):
    request.session.pop("username", None) # 세션에서 삽입한 username 제거
    return {"message": "로그아웃이 성공했습니다."}

"""
로그인 하면 쿠키값(세션키) 저장됨. 
로그아웃 하면 전송된 쿠키값으로 세션 제거.
"""

# 메모 생성
@router.post('/memos/')
async def create_memo(request:Request, memo:MemoCreate, db:AsyncSession=Depends(get_db)): # Depends -> 의존성 주입
    username = request.session.get('username')
    if username is None:
        raise HTTPException(status_code=401, detail='Not authorized')
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user in None:
        raise HTTPException(status_code=404, detail="User not Found")
    
    new_memo = Memo(title=memo.title, content=memo.content)

    # 엔티티를 직접 다루는 것이 아니라, 엔티티를 db 엔진 (db 세션)에 넣어서 db 엔진을 조작해야 함.
    db.add(new_memo)
    await db.commit()
    await db.refresh(new_memo) # DB에 저장된 값을 읽으면 입력하지 않은 id도 반환 받을 수 있음
    return ({"id": new_memo.id, "title": new_memo.title, "content": new_memo.content})

# 메모 조회
@router.get('/memos/')
async def list_memos(request: Request, db:AsyncSession=Depends(get_db)):
    username = request.session.get('username')
    if username is None:
        raise HTTPException(status_code=401, detail='Not authorized')
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user in None:
        raise HTTPException(status_code=404, detail="User not Found")
    
    result = await db.execute(select(Memo).where(Memo.user_id == user.id))
    memos = result.scalars().all() # 모든 memo 다 가져오기
    return templates.TemplateResponse('memos.html', {"memos": memos, "username": username})

#메모 수정
@router.put('/memos/{memo_id}')
async def update_memo(request: Request, memo_id:int, memo:MemoUpdate, db:AsyncSession=Depends(get_db)):
    username = request.session.get('username')
    if username is None:
        raise HTTPException(status_code=401, detail='Not authorized')
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user in None:
        raise HTTPException(status_code=404, detail="User not Found")
    
    # select 뒤에 where와 filter는 기능 동일. 이름만 차이?
    result = await db.execute(select(Memo).filter(User.id == user.id, Memo.id == memo_id))
    db_memo = result.scalars().first()
    #애초에 메모 검색 안되면 에러임
    if db_memo in None:
        return ({"error": "Memo not found"})
    
    if memo.title is not None:
        db_memo.title = memo.title

    if memo.content is not None:
        db_memo.content = memo.content

    await db.commit() #변경된 레코드를 바로 커밋
    await db.refresh(db_memo)

    return db_memo

# 메모 삭제
@router.delete('/memos/{memo_id}')
async def delete_memo(request: Request, memo_id:int, db:AsyncSession=Depends(get_db)): # Depends -> 의존성 주입
    username = request.session.get('username')
    if username is None:
        raise HTTPException(status_code=401, detail='Not authorized')
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user in None:
        raise HTTPException(status_code=404, detail="User not Found")
    
    result = await db.execute(select(Memo).filter(User.id == user.id, Memo.id == memo_id))
    db_memo = result.scalars().first()
    if db_memo in None:
        return ({"error": "Memo not found"})
    
    await db.delete(db_memo)
    await db.commit()
    
    return ({"mesage": "Memo deleted"})

@router.get('/about')
async def about():
    return {'message':'이것은 마이 메모 앱의 소개 페이지 입니다.'}
