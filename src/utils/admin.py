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
from src.schemas.human import Employee as HmEmployee
from src._utils import hash_password


def create_user_account(
    db_user: Session, db_human: Session, user_data: UserCreate
):
    user = User(
        Username=user_data.Username,
        Password=hash_password(user_data.Password),
        Role=user_data.Role.value,
        Employee_id=user_data.Employee_id,
    )

    employee = (
        db_human.query(HmEmployee)
        .filter(HmEmployee.EmployeeID == user_data.Employee_id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Id nhân viên không tồn tại")

    try:
        db_user.add(db_user)
        db_user.commit()
    except Exception as e:
        db_user.rollback()
        raise HTTPException(
            status_code=500, detail=f"Có lỗi khi tạo tài khoản: {str(e)}"
        )
    return {
        "username": user.Username,
        "role": user.Role.value,
        "employee_id": user.Employee_id,
    }


def update_user_account(
    db_user: Session, db_human: Session, username: str, user_data: UserUpdate
):
    user = db_user.query(User).filter(User.Username == username).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy tài khoản cần cập nhật"
        )

    try:
        if user_data.Password:
            user.Password = hash_password(user_data.Password)
        if user_data.Role:
            user.Role = user_data.Role
        if user_data.Employee_id:
            employee = (
                db_human.query(HmEmployee)
                .filter(HmEmployee.EmployeeID == user_data.Employee_id)
                .first()
            )
            if not employee:
                raise HTTPException(
                    status_code=404, detail="Id nhân viên không tồn tại"
                )
            user.Employee_id = user_data.Employee_id
        db_user.commit()
    except Exception as e:
        db_user.rollback()
        raise HTTPException(
            status_code=500, detail=f"Có lỗi khi cập nhật tài khoản: {str(e)}"
        )
    
    return {
        "username": user.Username,
        "role": user.Role,
        "employee_id": user.Employee_id,
    }
