from fastapi import Depends, Query
from fastapi.routing import APIRouter

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session

from ..schemas.user import User
from src.models.payroll import PayrollUpdate
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db

from ..utils.payroll import (
    get_payroll,
    get_attendance_records,
    update_payroll,
    search_payroll_logic
)
from .._utils import response


payroll_router = APIRouter(prefix="", tags=["Payroll"])


@payroll_router.get("")
def read_payroll(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    pr_db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=get_payroll(
            session=pr_db, 
            page=page, 
            per_page=per_page
        )
    )


@payroll_router.get("/search")
def search_payroll(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search_query: str = Query(None),
    pr_db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=search_payroll_logic(
            session=pr_db, 
            search_query=search_query,
            page=page, 
            per_page=per_page
        )
    )


@payroll_router.put("/update/{payroll_id}")
def update_payroll_router(
    payroll_id: int,
    update_data: PayrollUpdate,
    pr_db: Session = Depends(get_sync_pr_db)
):
    return update_payroll(
        session=pr_db, 
        payroll_id=payroll_id, 
        update_data=update_data)

@payroll_router.get("/attendance")
def read_attendance(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search_date: date = Query(None),
    employee_id: int = Query(None),
    pr_db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=get_attendance_records(
            session=pr_db, 
            page=page, 
            per_page=per_page, 
            search_date=search_date, 
            employee_id=employee_id
            )
    )

