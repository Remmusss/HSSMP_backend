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

from src.utils.profile import read_profile_logic

from src._utils import response


profile_router = APIRouter(prefix="", tags=["Profile"])

@profile_router.get("/")
def get_profile(
    db_user: Session = Depends(get_sync_user_db), 
    db_human: Session = Depends(get_sync_hm_db),
    db_payroll: Session = Depends(get_sync_pr_db),
    token: str = Depends(oauth2_scheme)
    ):
    return read_profile_logic(db_user, db_human, db_payroll, token)
