# pydentic

from typing import Optional
from pydantic import BaseModel

# signup dto
class UserCreate(BaseModel):
    username: str
    email: str
    password: str # 해시 전 패스워드

# login dto
class UserLogin(BaseModel):
    username: str
    password: str

# create memo dto
class MemoCreate(BaseModel): # memo create dto
    title: str
    content: str

#update memo dto
class MemoUpdate(BaseModel): # memo update dto
    title: Optional[str] = None #선택형. 기본값 설정
    content: Optional[str] = None
