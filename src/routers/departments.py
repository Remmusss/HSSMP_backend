from fastapi import Depends
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from sqlalchemy.orm import Session
from src._utils import response
from src.models.human import DepartmentCreate, DepartmentUpdate
from src.models.user import UserResponse
from src.utils.auth import has_role, get_current_user
from src.models.user import Role

from src.utils.departments import (
    read_departments,
    add_and_sync_department,
    update_and_sync_department,
    delete_and_sync_department,
)


departments_router = APIRouter(prefix="", tags=["Departments"])


@departments_router.get("")
def get_departments(
    db: Session = Depends(get_sync_hm_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value, Role.PAYROLL_MANAGER.value])
    )
):
    return response(data=read_departments(session=db))


@departments_router.post("/add")
def add_department(
    department: DepartmentCreate,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value])
    )
):
    return response(
        data=add_and_sync_department(
            session_human=hm_db, 
            session_payroll=pr_db, 
            department=department
        )
    )


@departments_router.put("/update/{department_id}")
def update_department(
    department_id: int,
    department: DepartmentUpdate,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value])
    )
):
    return response(
        data=update_and_sync_department(
            session_human=hm_db,
            session_payroll=pr_db,
            department_id=department_id,
            department=department,
        )
    )


@departments_router.delete("/delete/{department_id}")
def delete_department(
    department_id: int,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value])
    )
):
    return response(
        data=delete_and_sync_department(
            session_human=hm_db,
            session_payroll=pr_db,
            department_id=department_id
        )
    )
