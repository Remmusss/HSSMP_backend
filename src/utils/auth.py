from src.schemas.user import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.databases.user_db import get_sync_db as get_sync_user_db
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta, UTC

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
SECRET_KEY = "gi-cung-duoc"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.Username == username).first()
    if not user:
        return False
    if not verify_password(password, user.Password):
        return False
    return user


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str):
    user = db.query(User).filter(User.Username == username).first()
    return user


class TokenData(BaseModel):
    username: str | None = None


def get_current_user(
    db: Session = Depends(get_sync_user_db),
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Không thể xác thực tài khoản",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username == "":
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def has_role(required_roles: list[str]):
    def check_role(user: User = Depends(get_current_user)):
        if user.Role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền truy cập"
            )
        return user
    return check_role
