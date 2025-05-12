from fastapi import APIRouter, Depends, HTTPException, status, Form
from src.databases.user_db import get_sync_db as get_sync_user_db
from sqlalchemy.orm import Session
from src.utils.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    get_current_user,
)
from src.models.user import UserResponse

auth_router = APIRouter(prefix="", tags=["Auth"])


@auth_router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_sync_user_db),
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(data={"sub": user.Username})
    refresh_token = create_refresh_token(data={"sub": user.Username})

    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh")
def refresh(
    db: Session = Depends(get_sync_user_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_current_user(db, token)
    if not user:
        raise credentials_exception

    access_token = create_access_token(data={"sub": user.Username})
    refresh_token = create_refresh_token(data={"sub": user.Username})

    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.get("/me", response_model=UserResponse)
def me(db: Session = Depends(get_sync_user_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return UserResponse(
        Username=user.Username, Role=user.Role, Employee_id=user.Employee_id
    )
