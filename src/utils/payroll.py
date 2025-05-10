from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, String, extract
from ..schemas.human import (
    Employee as HREmployee,
    Department as HRDepartment,
    Dividend,
)
from ..schemas.payroll import (
    Employee as PREmployee,
    Department as PRDepartment,
    Salary,
    Attendance,
)
from ..models.payroll import SalaryReportByDepartment, AttendanceWarning, SalaryDifferenceWarning


from datetime import date, timedelta
from typing import Optional, List



def get_payroll(
        session: Session, 
        page: int = 1, 
        per_page: int = 10,
        search_date: date = None, 
        employee_id: int = None
        ):
    query = session.query(Salary).options(
        joinedload(Salary.employee)
        .joinedload(PREmployee.department),
        joinedload(Salary.employee)
        .joinedload(PREmployee.position)
    )


    if search_date:
        query = query.filter(
            extract('year', Salary.SalaryMonth) == search_date.year,
            extract('month', Salary.SalaryMonth) == search_date.month
        )

    if employee_id:
        query = query.filter(Salary.EmployeeID == employee_id)

    offset = (page - 1) * per_page
    results = query.order_by(Salary.SalaryMonth.desc()).offset(offset).limit(per_page).all()

    return results


def get_attendance_records(
        session: Session, 
        page: int = 1, 
        per_page: int = 10,
        search_date: Optional[date] = None, 
        employee_id: Optional[int] = None
        )-> List[Attendance]:
    query = session.query(Attendance).options(
        joinedload(Attendance.employee).joinedload(PREmployee.department),
        joinedload(Attendance.employee).joinedload(PREmployee.position)
    )

    if search_date:
        query = query.filter(
            extract('year', Attendance.AttendanceMonth) == search_date.year,
            extract('month', Attendance.AttendanceMonth) == search_date.month
        )

    if employee_id:
        query = query.filter(Attendance.EmployeeID == employee_id)

    offset = (page - 1) * per_page
    return query.order_by(Attendance.AttendanceMonth.desc()).offset(offset).limit(per_page).all()