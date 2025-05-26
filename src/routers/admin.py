from fastapi import APIRouter, Depends, HTTPException, status, Form
from src.databases.user_db import get_sync_db as get_sync_user_db
from src.databases.human_db import get_sync_db as get_sync_human_db
from sqlalchemy.orm import Session
from src.utils.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    get_current_user,
    has_role
)

from src.utils.admin import create_user_account, update_user_account
from src.models.user import UserCreate, UserUpdate, Role

from src._utils import response

admin_router = APIRouter(prefix="", tags=["Admin"])


@admin_router.post(
    "/create_user", description="Tạo tài khoản cho nhân viên bằng tài khoản ADMIN"
)
def create_user(
    user: UserCreate, 
    db_user: Session = Depends(get_sync_user_db),
    db_human: Session = Depends(get_sync_human_db),

    has_role=Depends(has_role(required_roles=[Role.ADMIN.value]))
):
    return response(
        message="Tài khoản đã được tạo thành công",
        data=create_user_account(db_user=db_user, db_human=db_human, user_data=user)
    )


@admin_router.put(
    "/update_user/{username}",
    description="Cập nhật tài khoản cho nhân viên bằng tài khoản ADMIN",
)
def update_user(
    username: str, 
    user: UserUpdate, 
    db_user: Session = Depends(get_sync_user_db),
    db_human: Session = Depends(get_sync_human_db),
    has_role=Depends(has_role(required_roles=[Role.ADMIN.value]))
):
    return response(
        message="Tài khoản đã được cập nhật thành công",
        data=update_user_account(db_user=db_user, db_human=db_human, username=username, user_data=user)
    )
