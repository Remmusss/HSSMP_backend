from sqlalchemy import delete, func, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select

from fastapi import HTTPException

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta

from .auth import get_current_user

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
    Position as PrPosition,
)

from ..utils.notifications import (
    upcoming_anniversaries,
    absent_days_warning,
    absent_days_warning_personal,
    salary_gap_warning,
    salary_gap_warning_personal,
)


def admin_dashboard_data_logic(
    session_human: Session, session_payroll: Session, session_user: Session, token: str
):
    try:
        total_employees = session_human.query(
            func.count(HmEmployee.EmployeeID)
        ).scalar()

        number_of_departments = session_human.query(
            func.count(HmDepartment.DepartmentID)
        ).scalar()

        payroll_total = session_payroll.query(func.sum(PrSalary.NetSalary)).scalar()

        number_of_notifications = (
            int(upcoming_anniversaries(session_human)["count"])
            + int(absent_days_warning(session_payroll)["count"])
            + int(
                absent_days_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
            + int(salary_gap_warning(session_payroll)["count"])
            + int(
                salary_gap_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
        )

        distribution_query = (
            session_human.query(
                HmDepartment.DepartmentID,
                HmDepartment.DepartmentName,
                func.count(HmEmployee.EmployeeID).label("Employee_count"),
            )
            .join(HmEmployee, HmDepartment.DepartmentID == HmEmployee.DepartmentID)
            .group_by(HmDepartment.DepartmentID, HmDepartment.DepartmentName)
        )

        results = distribution_query.order_by(desc("Employee_count")).all()

        department_distribution = [
            {
                "DepartmentID": dept_id,
                "DepartmentName": dept_name,
                "Employee_count": emp_count,
            }
            for dept_id, dept_name, emp_count in results
        ]

        attendance_query = (
            session_payroll.query(
                PrAttendance.AttendanceMonth,
                func.sum(PrAttendance.AbsentDays).label("AbsentDays"),
                func.sum(PrAttendance.LeaveDays).label("LeaveDays"),
                func.sum(PrAttendance.WorkDays).label("WorkDays"),
            )
            .group_by(PrAttendance.AttendanceMonth)
            .all()
        )

        attendance_overview = [
            {
                "AttendanceMonth": attendance.AttendanceMonth,
                "AbsentDays": attendance.AbsentDays,
                "LeaveDays": attendance.LeaveDays,
                "WorkDays": attendance.WorkDays,
            }
            for attendance in attendance_query
        ]
        return {
            "total_employees": total_employees,
            "number_of_departments": number_of_departments,
            "payroll_total": float(payroll_total) if payroll_total else 0,
            "number_of_notifications": number_of_notifications,
            "department_distribution": department_distribution,
            "attendance_overview": attendance_overview,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def hr_dashboard_data_logic(
    session_human: Session, session_payroll: Session, session_user: Session, token: str
):
    try:
        user = get_current_user(session_user, token)

        total_employees = session_human.query(
            func.count(HmEmployee.EmployeeID)
        ).scalar()

        number_of_departments = session_human.query(
            func.count(HmDepartment.DepartmentID)
        ).scalar()

        last_month_payroll = (
            session_payroll.query(PrSalary)
            .filter(PrSalary.EmployeeID == user.Employee_id)
            .order_by(PrSalary.SalaryMonth.desc())
            .first()
        )

        number_of_notifications = (
            int(upcoming_anniversaries(session_human)["count"])
            + int(absent_days_warning(session_payroll)["count"])
            + int(
                absent_days_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
            + int(
                salary_gap_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
        )
        distribution_query = (
            session_human.query(
                HmDepartment.DepartmentID,
                HmDepartment.DepartmentName,
                func.count(HmEmployee.EmployeeID).label("Employee_count"),
            )
            .join(HmEmployee, HmDepartment.DepartmentID == HmEmployee.DepartmentID)
            .group_by(HmDepartment.DepartmentID, HmDepartment.DepartmentName)
        )

        results = distribution_query.order_by(desc("Employee_count")).all()

        department_distribution = [
            {
                "DepartmentID": dept_id,
                "DepartmentName": dept_name,
                "Employee_count": emp_count,
            }
            for dept_id, dept_name, emp_count in results
        ]

        attendance_query = (
            session_payroll.query(
                PrAttendance.AttendanceMonth,
                func.sum(PrAttendance.AbsentDays).label("AbsentDays"),
                func.sum(PrAttendance.LeaveDays).label("LeaveDays"),
                func.sum(PrAttendance.WorkDays).label("WorkDays"),
            )
            .group_by(PrAttendance.AttendanceMonth)
            .all()
        )

        attendance_overview = [
            {
                "AttendanceMonth": attendance.AttendanceMonth,
                "AbsentDays": attendance.AbsentDays,
                "LeaveDays": attendance.LeaveDays,
                "WorkDays": attendance.WorkDays,
            }
            for attendance in attendance_query
        ]
        return {
            "total_employees": total_employees,
            "number_of_departments": number_of_departments,
            "last_month_payroll": (
                float(last_month_payroll.NetSalary) if last_month_payroll else None
            ),
            "number_of_notifications": number_of_notifications,
            "department_distribution": department_distribution,
            "attendance_overview": attendance_overview,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def payroll_dashboard_data_logic(
    session_human: Session, session_payroll: Session, session_user: Session, token: str
):
    try:
        user = get_current_user(session_user, token)
        employee = (
            session_payroll.query(PrEmployee)
            .filter(PrEmployee.EmployeeID == user.Employee_id)
            .first()
        )

        payroll_total = session_payroll.query(func.sum(PrSalary.NetSalary)).scalar()

        number_of_notifications = (
            int(upcoming_anniversaries(session_human)["count"])
            + int(
                salary_gap_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
            + int(
                absent_days_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
            + int(salary_gap_warning(session_payroll)["count"])
        )
        current_department = (
            session_payroll.query(PrDepartment)
            .filter(PrDepartment.DepartmentID == employee.DepartmentID)
            .first()
        )

        current_position = (
            session_payroll.query(PrPosition)
            .filter(PrPosition.PositionID == employee.PositionID)
            .first()
        )

        salary_query = (
            session_payroll.query(
                PrSalary.SalaryMonth, func.sum(PrSalary.NetSalary).label("TotalSalary")
            )
            .group_by(PrSalary.SalaryMonth)
            .all()
        )

        salary_distribution = [
            {
                "SalaryMonth": salary.SalaryMonth,
                "TotalSalary": salary.TotalSalary,
            }
            for salary in salary_query
        ]
        return {
            "EmployeeID": employee.EmployeeID if employee.EmployeeID else None,
            "payroll_total": float(payroll_total) if payroll_total else 0,
            "current_department": (
                current_department.DepartmentName if current_department else None
            ),
            "current_position": (
                current_position.PositionName if current_position else None
            ),
            "number_of_notifications": number_of_notifications,
            "salary_distribution": salary_distribution,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def employee_dashboard_data_logic(
    session_human: Session, session_payroll: Session, session_user: Session, token: str
):
    try:
        user = get_current_user(session_user, token)
        employee = (
            session_human.query(HmEmployee)
            .filter(HmEmployee.EmployeeID == user.Employee_id)
            .first()
        )

        last_month_payroll = (
            session_payroll.query(PrSalary)
            .filter(PrSalary.EmployeeID == employee.EmployeeID)
            .order_by(PrSalary.SalaryMonth.desc())
            .first()
        )

        number_of_notifications = (
            int(upcoming_anniversaries(session_human)["count"])
            + int(
                absent_days_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
            + int(
                salary_gap_warning_personal(session_user, session_payroll, token)[
                    "count"
                ]
            )
        )
        current_department = (
            session_payroll.query(PrDepartment)
            .filter(PrDepartment.DepartmentID == employee.DepartmentID)
            .first()
        )

        current_position = (
            session_payroll.query(PrPosition)
            .filter(PrPosition.PositionID == employee.PositionID)
            .first()
        )

        salary_query = (
            session_payroll.query(
                PrSalary.EmployeeID,
                PrSalary.SalaryMonth,
                func.sum(PrSalary.NetSalary).label("TotalSalary"),
            )
            .filter(PrSalary.EmployeeID == employee.EmployeeID)
            .group_by(PrSalary.EmployeeID, PrSalary.SalaryMonth)
            .all()
        )

        salary_distribution = [
            {
                "SalaryMonth": salary.SalaryMonth,
                "TotalSalary": salary.TotalSalary,
            }
            for salary in salary_query
        ]

        attendance_query = (
            session_payroll.query(PrAttendance)
            .filter(PrAttendance.EmployeeID == employee.EmployeeID)
            .order_by(PrAttendance.AttendanceMonth.desc())
            .limit(3)
            .all()
        )

        attendance_overview = [
            {
                "AttendanceMonth": attendance.AttendanceMonth,
                "AbsentDays": attendance.AbsentDays,
                "LeaveDays": attendance.LeaveDays,
                "WorkDays": attendance.WorkDays,
            }
            for attendance in attendance_query
        ]

        return {
            "EmployeeID": employee.EmployeeID if employee.EmployeeID else None,
            "LastMonthPayroll": (
                last_month_payroll.NetSalary if last_month_payroll else None
            ),
            "CurrentDepartment": (
                current_department.DepartmentName if current_department else None
            ),
            "CurrentPosition": (
                current_position.PositionName if current_position else None
            ),
            "NumberOfNotifications": number_of_notifications,
            "SalaryDistribution": salary_distribution,
            "AttendanceOverview": attendance_overview,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
