from sqlalchemy import func, desc, extract
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ..schemas.human import (
    Department as HmDepartment,
    Employee as HmEmployee,
    Dividend as HmDividend,
    Position as HmPosition,
)
from ..schemas.payroll import (
    Department as PrDepartment,
    Employee as PrEmployee,
    Salary as PrSalary,
    Attendance as PrAttendance,
)

from ..schemas.user import User
from src.utils.auth import get_current_user


def upcoming_anniversaries(session: Session, window_days: int = 30):
    today = datetime.today().date()
    upcoming = []

    employees = session.query(HmEmployee).all()

    for emp in employees:
        if not emp.HireDate:
            continue

        hire_date = emp.HireDate

        for milestone in [1, 5, 10, 15, 20, 25, 30]:
            anniversary_date = hire_date.replace(year=hire_date.year + milestone)
            delta = (anniversary_date - today).days

            upcoming_milestone = milestone + 5 if milestone % 5 == 0 else 5

            if 0 <= delta <= window_days:
                upcoming.append(
                    {
                        "EmployeeID": emp.EmployeeID,
                        "FullName": emp.FullName,
                        "MilestoneYears": milestone,
                        "JoinDate": hire_date.strftime("%Y-%m-%d"),
                        "AnniversaryDate": anniversary_date.strftime("%Y-%m-%d"),
                        "UpcomingMilestone": upcoming_milestone,
                    }
                )
                break

    return {
        "count": len(upcoming),
        "upcoming_anniversaries": upcoming if upcoming else "Không có thông báo",
    }


def absent_days_warning(session: Session, windows_month: int = 3):
    today = datetime.today().date()
    warnings = []

    attendance = session.query(PrAttendance).all()

    for att in attendance:
        absent_days = att.AbsentDays
        leave_days = att.LeaveDays

        month_notification = today.month - att.AttendanceMonth.month

        if absent_days > leave_days and month_notification <= windows_month:
            warnings.append(
                {
                    "EmployeeID": att.EmployeeID,
                    "AllowedLeaveDays": leave_days,
                    "TakenLeaveDays": absent_days,
                    "ExcessDays": absent_days - leave_days,
                    "AttendanceMonth": att.AttendanceMonth.strftime("%Y-%m-%d"),
                }
            )

    return {
        "count": len(warnings),
        "absent_days_warning": warnings if warnings else "Không có thông báo",
    }


def absent_days_warning_personal(
    db_user: Session, db_payroll: Session, token: str, windows_month: int = 3
):
    user = get_current_user(db_user, token)

    credentials_exception = HTTPException(
        status_code=401,
        detail="Không thể xác thực tài khoản",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise credentials_exception

    today = datetime.today().date()
    warnings = []

    attendance = (
        db_payroll.query(PrAttendance)
        .filter(PrAttendance.EmployeeID == user.Employee_id)
        .all()
    )

    for att in attendance:
        absent_days = att.AbsentDays
        leave_days = att.LeaveDays

        month_notification = today.month - att.AttendanceMonth.month

        if absent_days > leave_days and month_notification <= windows_month:
            warnings.append(
                {
                    "EmployeeID": att.EmployeeID,
                    "AllowedLeaveDays": leave_days,
                    "TakenLeaveDays": absent_days,
                    "ExcessDays": absent_days - leave_days,
                    "AttendanceMonth": att.AttendanceMonth.strftime("%Y-%m-%d"),
                }
            )

    return {
        "count": len(warnings),
        "absent_days_warning": warnings if warnings else "Không có thông báo",
    }


def salary_gap_warning(session: Session, allowed_gap_percentage: int = 30):
    warnings = []

    employees = session.query(PrEmployee).options(joinedload(PrEmployee.salaries)).all()

    for employee in employees:
        salaries = (
            session.query(PrSalary)
            .filter(PrSalary.EmployeeID == employee.EmployeeID)
            .order_by(PrSalary.SalaryMonth.desc())
            .limit(2)
            .all()
        )

        if len(salaries) < 2:
            continue

        current_salary = salaries[0].NetSalary
        previous_salary = salaries[1].NetSalary

        if previous_salary or previous_salary > 0:
            gap_percentage = (current_salary - previous_salary) / previous_salary * 100

            if abs(gap_percentage) >= allowed_gap_percentage:
                warnings.append(
                    {
                        "EmployeeID": employee.EmployeeID,
                        "EmployeeName": employee.FullName,
                        "CurrentSalary": current_salary,
                        "PreviousSalary": previous_salary,
                        "GapPercentage": round(gap_percentage, 2),
                        "CurrentMonth": salaries[0].SalaryMonth.strftime("%Y-%m-%d"),
                        "PreviousMonth": salaries[1].SalaryMonth.strftime("%Y-%m-%d"),
                    }
                )

    return {
        "count": len(warnings),
        "salary_gap_warning": warnings if warnings else "Không có thông báo",
    }


def salary_gap_warning_personal(
    db_user: Session, db_payroll: Session, token: str, allowed_gap_percentage: int = 30
):
    user = get_current_user(db_user, token)

    credentials_exception = HTTPException(
        status_code=401,
        detail="Không thể xác thực tài khoản",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise credentials_exception

    warnings = []

    salaries = (
        db_payroll.query(PrSalary)
        .filter(PrSalary.EmployeeID == user.Employee_id)
        .order_by(PrSalary.SalaryMonth.desc())
        .limit(2)
        .all()
    )

    if len(salaries) < 2:
        return {"salary_gap_warning": "Không có thông báo"}

    current_salary = salaries[0].NetSalary
    previous_salary = salaries[1].NetSalary

    gap_percentage = (current_salary - previous_salary) / previous_salary * 100

    if abs(gap_percentage) >= allowed_gap_percentage:
        employee = (
            db_payroll.query(PrEmployee)
            .filter(PrEmployee.EmployeeID == user.Employee_id)
            .first()
        )
        employee_name = employee.FullName if employee else user.FullName

        warnings.append(
            {
                "EmployeeID": user.Employee_id,
                "EmployeeName": employee_name,
                "CurrentSalary": current_salary,
                "PreviousSalary": previous_salary,
                "GapPercentage": round(gap_percentage, 2),
                "CurrentMonth": salaries[0].SalaryMonth.strftime("%Y-%m-%d"),
                "PreviousMonth": salaries[1].SalaryMonth.strftime("%Y-%m-%d"),
            }
        )

    return {
        "count": len(warnings),
        "salary_gap_warning": warnings if warnings else "Không có thông báo",
    }
