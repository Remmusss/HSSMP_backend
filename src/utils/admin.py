from src.schemas.user import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.databases.user_db import get_sync_db as get_sync_user_db
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta, UTC

from src.models.user import UserCreate, UserUpdate

from src._utils import hash_password



def create_user_account(session: Session, user: UserCreate):
    db_user = User(
        Username=user.Username,
        Password=hash_password(user.Password),
        Role=user.Role.value,
        Employee_id=user.Employee_id,
    )
    try:
        session.add(db_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Có lỗi khi tạo tài khoản: {str(e)}"
        )
    return {
        "username": user.Username,
        "role": user.Role.value,
        "employee_id": user.Employee_id,
    }


def update_user_account(session: Session, username: str, user: UserUpdate):
    db_user = session.query(User).filter(User.Username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản cần cập nhật")

    try:
        if user.Password:
            db_user.Password = hash_password(user.Password)
        if user.Role:
            db_user.Role = user.Role
        if user.Employee_id:
            db_user.Employee_id = user.Employee_id
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Có lỗi khi cập nhật tài khoản: {str(e)}")
    return {
        "username": db_user.Username,
        "role": db_user.Role,
        "employee_id": db_user.Employee_id,
    }
