from sqlalchemy import delete, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select

from fastapi import HTTPException

from typing import Optional, List
from datetime import date, datetime, timedelta

from ..schemas.human import (
    Department as HmDepartment,
    Employee as HmEmployee,
    Dividend as HmDividend,
    Position as HmPosition
)
from ..schemas.payroll import (
    Department as PrDepartment,
    Employee as PrEmployee,
    Salary as PrSalary,
    Attendance as PrAttendance
)

def read_departments(session: Session):
    employee_count_subquery = (
        session.query(
            HmEmployee.DepartmentID,
            func.count(HmEmployee.EmployeeID).label("employee_count")
        )
        .group_by(HmEmployee.DepartmentID)
        .subquery()
    )
    
    query = (
        session.query(
            HmDepartment,
            func.coalesce(employee_count_subquery.c.employee_count, 0).label("employee_count")
        )
        .outerjoin(
            employee_count_subquery,
            HmDepartment.DepartmentID == employee_count_subquery.c.DepartmentID
        )
    )
    
    results = query.order_by(HmDepartment.DepartmentID).all()
    
    return [
        {
            "DepartmentID": dept.DepartmentID,
            "DepartmentName": dept.DepartmentName,
            "NumbersOfEmployees": employee_count,
            "CreatedAt": dept.CreatedAt,
            "UpdatedAt": dept.UpdatedAt
        }
        for dept, employee_count in results
    ]
