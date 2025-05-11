from fastapi import Depends, Query
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from sqlalchemy.orm import Session
from src.schemas.user import User
from src.utils.employees import (
    get_employees,
    add_and_sync_employee,
    search_employees_logic,
    view_employee_details_logic,
    update_and_sync_employee,
    delete_employee_logic
)
from src.models.human import EmployeeCreate, EmployeeUpdate
from src._utils import response

from typing import Optional

employees_router = APIRouter(prefix="", tags=["Employees"])




@employees_router.get("")
def read_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_sync_hm_db)
):

    return response(
        data=get_employees(session=db, page=page, per_page=per_page)
        )


@employees_router.get("/search")
def search_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search_query: str = Query(None),
    db: Session = Depends(get_sync_hm_db)
):
    return response(
        data=search_employees_logic(
            session=db,
            search_query=search_query,
            page=page,
            per_page=per_page
        )
    )


@employees_router.post("/add")
def add_employee(
    employee: EmployeeCreate,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=add_and_sync_employee(
            session_human=hm_db,
            session_payroll=pr_db,
            employee=employee
        )
    )

@employees_router.put("/update/{employee_id}")
def update_employee(
    employee_id: int,
    update_data: EmployeeUpdate,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=update_and_sync_employee(
            session_human=hm_db,
            session_payroll=pr_db,
            employee_id=employee_id,
            update_data=update_data
        )
    )

@employees_router.delete("/delete/{employee_id}")
def delete_employee(
    employee_id: int,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=delete_employee_logic(
            session_human=hm_db, 
            session_payroll=pr_db, 
            employee_id=employee_id
        )
    )

@employees_router.get("/details/{employee_id}")
def view_employee_details(
    employee_id: int,
    db: Session = Depends(get_sync_hm_db)
):
    return response(
        data=view_employee_details_logic(session=db, employee_id=employee_id)
    )