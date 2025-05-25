from fastapi import Depends, Query
from fastapi.routing import APIRouter
from src.databases.user_db import get_sync_db as get_sync_user_db
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from sqlalchemy.orm import Session
from src.schemas.user import User
from src.utils.dashboard import (
    admin_dashboard_data_logic,
    hr_dashboard_data_logic,
    payroll_dashboard_data_logic,
    employee_dashboard_data_logic,
)
from src.models.human import EmployeeCreate, EmployeeUpdate
from src._utils import response
from src.utils.auth import has_role, oauth2_scheme
from src.models.user import Role

from typing import Optional

dashboard_router = APIRouter(prefix="", tags=["Dashboard"])


@dashboard_router.get("/admin")
def dashboard_data(
    session_payroll: Session = Depends(get_sync_pr_db),
    session_human: Session = Depends(get_sync_hm_db),
    session_user: Session = Depends(get_sync_user_db),
    token: str = Depends(oauth2_scheme),
    has_role = Depends(has_role(Role.ADMIN.value))
):
    data = admin_dashboard_data_logic(
        session_human=session_human,
        session_payroll=session_payroll,
        session_user=session_user,
        token=token
    )

    return response(data=data)

@dashboard_router.get("/hr-manager")
def hr_dashboard_data(
    session_payroll: Session = Depends(get_sync_pr_db),
    session_human: Session = Depends(get_sync_hm_db),
    session_user: Session = Depends(get_sync_user_db),
    token: str = Depends(oauth2_scheme),
    has_role = Depends(has_role(Role.HR_MANAGER.value))
):
    data = hr_dashboard_data_logic(
        session_human=session_human,
        session_payroll=session_payroll,
        session_user=session_user,
        token=token
    )

    return response(data=data)

@dashboard_router.get("/payroll-manager")
def payroll_dashboard_data(
    session_human: Session = Depends(get_sync_hm_db),
    session_payroll: Session = Depends(get_sync_pr_db),
    session_user: Session = Depends(get_sync_user_db),
    token: str = Depends(oauth2_scheme),
    has_role = Depends(has_role(Role.PAYROLL_MANAGER.value))
):
    data = payroll_dashboard_data_logic(
        session_human=session_human,
        session_payroll=session_payroll,
        session_user=session_user,
        token=token
    )

    return response(data=data)

@dashboard_router.get("/employee")
def employee_dashboard_data(
    session_human: Session = Depends(get_sync_hm_db),
    session_payroll: Session = Depends(get_sync_pr_db),
    session_user: Session = Depends(get_sync_user_db),
    token: str = Depends(oauth2_scheme),
    has_role = Depends(has_role(Role.EMPLOYEE.value))
):
    data = employee_dashboard_data_logic(
        session_human=session_human,
        session_payroll=session_payroll,
        session_user=session_user,
        token=token
    )

    return response(data=data)

