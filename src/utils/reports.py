from sqlalchemy import func, desc, extract
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

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

def get_hr_report_logic(session: Session):
    total_employees = session.query(func.count(HmEmployee.EmployeeID)).scalar()
    
    department_allocation = (
        session.query(
            HmDepartment.DepartmentID,
            HmDepartment.DepartmentName,
            func.count(HmEmployee.EmployeeID).label("employee_count")
        )
        .outerjoin(HmEmployee, HmDepartment.DepartmentID == HmEmployee.DepartmentID)
        .group_by(HmDepartment.DepartmentID, HmDepartment.DepartmentName)
        .order_by(desc("employee_count"))
        .all()
    )
    
    position_allocation = (
        session.query(
            HmPosition.PositionID,
            HmPosition.PositionName,
            func.count(HmEmployee.EmployeeID).label("employee_count")
        )
        .outerjoin(HmEmployee, HmPosition.PositionID == HmEmployee.PositionID)
        .group_by(HmPosition.PositionID, HmPosition.PositionName)
        .order_by(desc("employee_count"))
        .all()
    )
    
    status_allocation = (
        session.query(
            HmEmployee.Status,
            func.count(HmEmployee.EmployeeID).label("employee_count")
        )
        .group_by(HmEmployee.Status)
        .order_by(desc("employee_count"))
        .all()
    )
    
    return {
        "total_employees": total_employees,
        "department_allocation": [
            {
                "department_id": dept_id,
                "department_name": dept_name,
                "employee_count": emp_count,
                "percentage": round((emp_count / total_employees * 100), 2) if total_employees > 0 else 0
            }
            for dept_id, dept_name, emp_count in department_allocation
        ],
        "position_allocation": [
            {
                "position_id": pos_id,
                "position_name": pos_name,
                "employee_count": emp_count,
                "percentage": round((emp_count / total_employees * 100), 2) if total_employees > 0 else 0
            }
            for pos_id, pos_name, emp_count in position_allocation
        ],
        "status_allocation": [
            {
                "status": status if status else "Unknown",
                "employee_count": emp_count,
                "percentage": round((emp_count / total_employees * 100), 2) if total_employees > 0 else 0
            }
            for status, emp_count in status_allocation
        ]
    }

def get_payroll_report_logic(session: Session, month: Optional[date] = None):
    salary_query = (
        session.query(
            func.sum(PrSalary.NetSalary).label("total_budget"),
            func.count(PrSalary.SalaryID).label("total_salary_count")
        )
    )
    
    dept_query = (
        session.query(
            PrDepartment.DepartmentID, 
            PrDepartment.DepartmentName,
            func.count(PrSalary.SalaryID).label("total_salary_count"),
            func.sum(PrSalary.NetSalary).label("total_salary"),
            func.avg(PrSalary.NetSalary).label("average_salary")
        )
        .join(PrEmployee, PrDepartment.DepartmentID == PrEmployee.DepartmentID)
        .join(PrSalary, PrEmployee.EmployeeID == PrSalary.EmployeeID)
    )
    
    if month:
        salary_query = salary_query.filter(
            extract('year', PrSalary.SalaryMonth) == month.year,
            extract('month', PrSalary.SalaryMonth) == month.month
        )
        dept_query = dept_query.filter(
            extract('year', PrSalary.SalaryMonth) == month.year,
            extract('month', PrSalary.SalaryMonth) == month.month
        )
        report_title = month.strftime("%m/%Y")
    else:
        report_title = "Tất cả thời gian"
    
    salary_stats = salary_query.first()
    total_budget = salary_stats.total_budget or 0
    total_salary_count = salary_stats.total_salary_count or 0
    
    average_salary = float(total_budget) / total_salary_count if total_salary_count > 0 else 0
    
    avg_salary_by_dept = dept_query.group_by(
        PrDepartment.DepartmentID, PrDepartment.DepartmentName
    ).all()
    
    return {
        "report_period": report_title,
        "total_budget": float(total_budget),
        "average_salary": round(average_salary, 2),
        "total_salary_count": total_salary_count,
        "department_analysis": [
            {
                "department_id": dept_id,
                "department_name": dept_name,
                "total_salary_department_count": salary_count,
                "total_salary": float(total_salary),
                "average_salary": float(avg_salary),
                "budget_percentage": round((float(total_salary) / float(total_budget) * 100), 2) if total_budget > 0 else 0
            }
            for dept_id, dept_name, salary_count, total_salary, avg_salary in avg_salary_by_dept
        ]
    }

def get_dividend_report_logic(session: Session, year: Optional[int] = None):
    total_dividend_query = session.query(func.sum(HmDividend.DividendAmount).label("total_dividend"))
    employee_count_query = session.query(func.count(func.distinct(HmDividend.EmployeeID)))
    
    base_query = (
        session.query(
            HmEmployee.EmployeeID,
            HmEmployee.FullName,
            HmDepartment.DepartmentName,
            HmPosition.PositionName,
            func.sum(HmDividend.DividendAmount).label("total_dividend"),
            func.count(HmDividend.DividendID).label("dividend_count")
        )
        .join(HmDividend, HmEmployee.EmployeeID == HmDividend.EmployeeID)
        .join(HmDepartment, HmEmployee.DepartmentID == HmDepartment.DepartmentID, isouter=True)
        .join(HmPosition, HmEmployee.PositionID == HmPosition.PositionID, isouter=True)
    )
    
    if year:
        total_dividend_query = total_dividend_query.filter(extract('year', HmDividend.DividendDate) == year)
        employee_count_query = employee_count_query.filter(extract('year', HmDividend.DividendDate) == year)
        base_query = base_query.filter(extract('year', HmDividend.DividendDate) == year)
        report_title = f"Năm {year}"
    else:
        report_title = "Tất cả các năm"
    
    total_dividend = total_dividend_query.scalar() or 0
    employee_count = employee_count_query.scalar() or 0
    
    employees_with_shares = (
        base_query.group_by(
            HmEmployee.EmployeeID, 
            HmEmployee.FullName, 
            HmDepartment.DepartmentName, 
            HmPosition.PositionName
        )
        .order_by(desc("total_dividend"))
        .all()
    )
    
    return {
        "report_period": report_title,
        "total_dividend_paid": float(total_dividend),
        "employee_count": employee_count,
        "employees_with_shares": [
            {
                "employee_id": emp_id,
                "employee_name": emp_name,
                "department": dept_name if dept_name else "N/A",
                "position": pos_name if pos_name else "N/A",
                "total_dividend": float(total_div),
                "dividend_count": div_count,  # Số lần nhận cổ tức
                "percentage": round((float(total_div) / float(total_dividend) * 100), 2) if total_dividend > 0 else 0
            }
            for emp_id, emp_name, dept_name, pos_name, total_div, div_count in employees_with_shares
        ]
    }
