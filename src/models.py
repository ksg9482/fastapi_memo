from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200))
    hasd_password = Column(String(512))

class Memo(Base):
    __tablename__ = 'memo'
    id = Column(Integer, primary_key=True, index=True) # primary_key 선언하면 자동으로 Index 되지만 관례상
    title = Column(String(100))
    content = Column(String(1000))