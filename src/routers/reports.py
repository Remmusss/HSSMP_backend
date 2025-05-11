from fastapi import Depends, Query
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from src.utils.reports import get_hr_report_logic, get_payroll_report_logic, get_dividend_report_logic
from src._utils import response

reports_router = APIRouter(prefix="", tags=["Reports"])

@reports_router.get("/hr")
def get_hr_report_endpoint(
    db: Session = Depends(get_sync_hm_db)
):

    return response(
        data=get_hr_report_logic(session=db)
    )

@reports_router.get("/payroll")
def get_payroll_report(
    month: Optional[date] = Query(None, description="Tháng báo cáo (format: YYYY-MM-DD)"),
    db: Session = Depends(get_sync_pr_db)
):
    return response(
        data=get_payroll_report_logic(session=db, month=month)
    )

@reports_router.get("/dividend")
def get_dividend_report_endpoint(
    year: Optional[int] = Query(None, description="Năm báo cáo"),
    db: Session = Depends(get_sync_hm_db)
):
    return response(
        data=get_dividend_report_logic(session=db, year=year)
    )
