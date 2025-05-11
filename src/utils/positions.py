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

def read_positions(session: Session):
    employee_count_subquery = (
        session.query(
            HmEmployee.PositionID,
            func.count(HmEmployee.EmployeeID).label("employee_count")
        )
        .group_by(HmEmployee.PositionID)
        .subquery()
    )
    
    query = (
        session.query(
            HmPosition,
            func.coalesce(employee_count_subquery.c.employee_count, 0).label("employee_count")
        )
        .outerjoin(
            employee_count_subquery,
            HmPosition.PositionID == employee_count_subquery.c.PositionID
        )
    )
    
    results = query.order_by(HmPosition.PositionID).all()
    
    return [
        {
            "PositionID": position.PositionID,
            "PositionName": position.PositionName,
            "TotalEmployees": employee_count,
            "CreatedAt": position.CreatedAt,
            "UpdatedAt": position.UpdatedAt
        }
        for position, employee_count in results
    ]

def get_position_distribution(session: Session, position_id: int):
    position = session.query(HmPosition).filter_by(PositionID=position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Chức vụ không tồn tại")
    
    distribution_query = (
        session.query(
            HmDepartment.DepartmentID,
            HmDepartment.DepartmentName,
            func.count(HmEmployee.EmployeeID).label("employee_count")
        )
        .join(
            HmEmployee,
            HmDepartment.DepartmentID == HmEmployee.DepartmentID
        )
        .filter(HmEmployee.PositionID == position_id)
        .group_by(HmDepartment.DepartmentID, HmDepartment.DepartmentName)
    )
    
    results = distribution_query.order_by(HmDepartment.DepartmentName).all()
    
    return {
        "PositionID": position.PositionID,
        "PositionName": position.PositionName,
        "TotalEmployees": sum(emp_count for _, _, emp_count in results),
        "DepartmentDistribution": [
            {
                "DepartmentID": dept_id,
                "DepartmentName": dept_name,
                "EmployeeCount": emp_count
            }
            for dept_id, dept_name, emp_count in results
        ]
    }

