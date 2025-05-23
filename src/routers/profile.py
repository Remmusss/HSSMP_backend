from fastapi import Depends, Query
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from src.databases.user_db import get_sync_db as get_sync_user_db
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.utils.auth import has_role
from src.models.user import Role
from src.utils.auth import oauth2_scheme

from src.utils.profile import read_profile_logic, change_password_logic

from src._utils import response


profile_router = APIRouter(prefix="", tags=["Profile"])


@profile_router.get("/")
def get_profile(
    db_user: Session = Depends(get_sync_user_db),
    db_human: Session = Depends(get_sync_hm_db),
    db_payroll: Session = Depends(get_sync_pr_db),
    token: str = Depends(oauth2_scheme),
):
    return response(
        data=read_profile_logic(
            db_user=db_user, db_human=db_human, db_payroll=db_payroll, token=token
        )
    )


@profile_router.put("/change_password")
def change_password(
    old_password: str,    
    new_password: str,
    session: Session = Depends(get_sync_user_db),
    token: str = Depends(oauth2_scheme),
):
    return response(
        message="Mật khẩu đã được cập nhật thành công",
        data=change_password_logic(
            session=session,
            token=token,
            old_password=old_password,
            new_password=new_password,
        ),
    )
