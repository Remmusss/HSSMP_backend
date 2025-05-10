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

    employee_id: Mapped[int] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String(50), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50))
