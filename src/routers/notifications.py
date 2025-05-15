from fastapi import Depends, Query
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from src.databases.user_db import get_sync_db as get_sync_user_db
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from src.utils.notifications import (
    upcoming_anniversaries,
    absent_days_warning,
    absent_days_personal_warning,
    salary_gap_warning,
    salary_gap_warning_personal,
)
from src._utils import response
from src.utils.auth import has_role
from src.models.user import Role
from src.utils.auth import oauth2_scheme

notifications_router = APIRouter(prefix="", tags=["Notifications"])


@notifications_router.get(
    "/anniversaries",
    description="Lấy thông báo về ngày kỷ niệm của nhân viên sắp tới trong 30 ngày",
)
def get_upcoming_anniversaries(db: Session = Depends(get_sync_hm_db)):
    return response(data=upcoming_anniversaries(session=db))


@notifications_router.get(
    "/absent-days-warning",
    description="Lấy thông báo về số ngày nghỉ phép của TẤT CẢ nhân viên trong 3 tháng gần đây (cho quản lý dùng)",
)
def get_absent_days_warning(
    db: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(
            required_roles=[
                Role.ADMIN.value,
                Role.HR_MANAGER.value,
                Role.PAYROLL_MANAGER.value,
            ]
        )
    ),
):
    return response(data=absent_days_warning(session=db))


@notifications_router.get(
    "/absent-days-personal-warning",
    description="Lấy thông báo về số ngày nghỉ phép của nhân viên trong 3 tháng gần đây",
)
def get_absent_days_personal_warning(
    db_user: Session = Depends(get_sync_user_db),
    db_payroll: Session = Depends(get_sync_pr_db),
    token: str = Depends(oauth2_scheme),
):
    return response(
        data=absent_days_personal_warning(
            db_user=db_user, db_payroll=db_payroll, token=token
        )
    )


@notifications_router.get(
    "/salary-gap-warning",
    description="Lấy thông báo về sự chênh lệch lương giữa 2 tháng gần đây của TẤT CẢ nhân viên",
)
def get_salary_gap_warning(
    db_payroll: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(
            required_roles=[
                Role.ADMIN.value,
                Role.HR_MANAGER.value,
                Role.PAYROLL_MANAGER.value,
            ]
        )
    ),
):
    return response(data=salary_gap_warning(session=db_payroll))

@notifications_router.get(
    "/salary-gap-warning-personal",
    description="Lấy thông báo về sự chênh lệch lương giữa 2 tháng gần đây của bản thân",
)
def get_salary_gap_warning_personal(
    db_user: Session = Depends(get_sync_user_db),
    db_payroll: Session = Depends(get_sync_pr_db),
    token: str = Depends(oauth2_scheme),
):
    return response(
        data=salary_gap_warning_personal(
            db_user=db_user, db_payroll=db_payroll, token=token
        )
    )
