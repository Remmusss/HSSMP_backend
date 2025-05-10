from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from src.core.config import sqlserver_conf

DATABASE_URL = sqlserver_conf.SQLSERVER_CONNECTION

engine = create_engine(DATABASE_URL, echo=True)


SessionLocal = sessionmaker(
    engine, 
    class_=Session, 
    expire_on_commit=False
)

def get_sync_db():
    with SessionLocal() as session:
        yield session
