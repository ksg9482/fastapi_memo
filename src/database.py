from sqlalchemy.orm import Session, sessionmaker #DB 접속
# from sqlalchemy import create_engine #동기 구조
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

# DATABASE_URL = "mysql+pymysql://root:root@localhost/fastapi_memo"
DATABASE_URL = "mysql+aiomysql://root:root@localhost/fastapi_memo"
# aiomysql -> 비동기 지원
engine = create_async_engine(DATABASE_URL, echo=True) # echo -> 내부에서 어떻게 동작하는지 확인용. 디버깅

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine,
    class_=AsyncSession # class_ -> 언더바까지 포함.
    )

Base = declarative_base() # 베이스 선언. sqlalchemy orm을 이용하기 위한 root 상속
