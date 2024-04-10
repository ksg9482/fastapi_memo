from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {
        "request": request #TemplateResponse하려면 request: Request를 기본적으로 받음. 
        })

@app.get('/about')
async def about():
    return {'message':'이것은 마이 메모 앱의 소개 페이지 입니다.'}
