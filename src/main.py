from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware #세션 관리
from database import Base, engine
from controllers import router
from contextlib import asynccontextmanager
import uvicorn

# 동기적으로 실행시 테이블 만드는 코드
# Base.metadata.create_all(bind=engine) # 자동으로 테이블 생성

# DB 비동기 실행. 비동기로 함수 실행.
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # app 시작시 실행될 로직. 앱 실행시 비동기적으로 DB 연결되면 테이블 생성 함수 연동해서 실행 
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield # 비동기로 처리하고 양보해서 이후 처리 하도록 함
    # app 종료시 실행될 로직 (팔요한 경우)

# fastapi 앱 초기화
app = FastAPI(lifespan=app_lifespan, docs_url=None, redoc_url=None) 
# lifespan에 함수를 넣어서 동작시 함수를 실행하도록 함
# docs, redoc url을 막아서 사용자가 접근하지 못하게 함
app.include_router(router)

session_secret = '1234567890'
app.add_middleware(SessionMiddleware, secret_key=session_secret) # 세션 미들웨어 삽입

templates = Jinja2Templates(directory="templates")

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {
        "request": request #TemplateResponse하려면 request: Request를 기본적으로 받음. 
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
