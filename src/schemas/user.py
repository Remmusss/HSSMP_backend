from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import ForeignKey, String, Boolean, JSON, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from ..databases.user_db import engine
from sqlalchemy import Table, Column


class Base(DeclarativeBase):
    pass

def create_tables():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)

class User(Base):
    __tablename__ = 'Users'
    
    Employee_id: Mapped[int] = mapped_column(Integer)
    Username: Mapped[str] = mapped_column(String(50), primary_key=True)
    Password: Mapped[str] = mapped_column(String(255), nullable=False)
    Role: Mapped[str] = mapped_column(String(50))
