from fastapi import Depends
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from sqlalchemy.orm import Session
from src.utils.departments import read_departments
from src._utils import response

departments_router = APIRouter(prefix="", tags=["Departments"])

@departments_router.get("")
def get_departments(
    db: Session = Depends(get_sync_hm_db)
):
    return response(
        data=read_departments(
            session=db
        )
    )
