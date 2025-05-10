from fastapi import Depends, Query
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hr_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from sqlalchemy.orm import Session
from src.schemas.user import User
from src.utils.employees import (
    get_employees,
    add_and_sync_employee,
    search_employees_logic
)
from src.models.human import EmployeeCreate, EmployeeUpdate
from src._utils import response

from typing import Optional

employees_router = APIRouter(prefix="", tags=["Employees"])




@employees_router.get("")
def read_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_sync_hr_db)
):

    return response(
        data=get_employees(session=db, page=page, per_page=per_page)
        )


@employees_router.get("/search")
def search_employees(
    db: Session = Depends(get_sync_hr_db),
    search_query: str = Query(None)
):
    return response(
        data=search_employees_logic(
            session=db,
            search_query=search_query
        )
    )


@employees_router.post("/add")
def add_employee(
    employee: EmployeeCreate,
    hr_db: Session = Depends(get_sync_hr_db),
    pr_db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=add_and_sync_employee(
            session_human=hr_db,
            session_payroll=pr_db,
            employee=employee
        )
    )

