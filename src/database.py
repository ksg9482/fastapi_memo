from sqlalchemy.orm import Session, sessionmaker #DB 접속
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String #DB 테이블 정의
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "mysql+pymysql://root:root@localhost/fastapi_memo"
engine = create_engine(DATABASE_URL) # DB 접속

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # 베이스 선언. sqlalchemy orm을 이용하기 위한 root 상속
