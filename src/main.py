from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware #세션 관리
from database import Base, engine
from controllers import router
import uvicorn


app = FastAPI()
app.include_router(router)

session_secret = '1234567890'
app.add_middleware(SessionMiddleware, secret_key=session_secret) # 세션 미들웨어 삽입

Base.metadata.create_all(bind=engine) # 자동으로 테이블 생성

templates = Jinja2Templates(directory="templates")

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {
        "request": request #TemplateResponse하려면 request: Request를 기본적으로 받음. 
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
