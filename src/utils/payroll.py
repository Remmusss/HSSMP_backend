from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, String, extract
from ..schemas.human import (
    Employee as HmEmployee,
    Department as HmDepartment,
    Dividend as HmDividend,
)
from ..schemas.payroll import (
    Employee as PrEmployee,
    Department as PrDepartment,
    Salary as PrSalary,
    Attendance as PrAttendance,
)
from ..models.payroll import ( 
    SalaryReportByDepartment, 
    AttendanceWarning, 
    SalaryDifferenceWarning, 
    PayrollUpdate
)

from datetime import date, timedelta
from typing import Optional, List



def get_payroll(
        session: Session, 
        page: int = 1, 
        per_page: int = 10
        ):
    query = session.query(PrSalary).join(
        PrEmployee, PrSalary.EmployeeID == PrEmployee.EmployeeID
    )

    offset = (page - 1) * per_page
    results = query.order_by(PrSalary.SalaryMonth.desc()).offset(offset).limit(per_page).all()

    return [
        {
            "EmployeeID": salary.EmployeeID,
            "SalaryID": salary.SalaryID,
            "FullName": salary.employee.FullName,
            "SalaryMonth": salary.SalaryMonth,
            "BaseSalary": salary.BaseSalary,
            "Bonus": salary.Bonus,
            "Deductions": salary.Deductions,
            "NetSalary": salary.NetSalary,
            "Status": salary.employee.Status
        }
        for salary in results
    ]


def search_payroll_logic(
        session: Session, 
        search_query: str = None,
        page: int = 1,
        per_page: int = 10
        ):
    query = session.query(PrSalary).join(
        PrEmployee, PrSalary.EmployeeID == PrEmployee.EmployeeID
    )

    if search_query:
        try:
            numeric_query = int(search_query)
            query = query.filter(
                (PrEmployee.EmployeeID == numeric_query) |
                (PrSalary.SalaryID == numeric_query) |
                (PrEmployee.FullName.ilike(f"%{search_query}%"))
            )
        except ValueError:
            query = query.filter(
                (PrEmployee.FullName.ilike(f"%{search_query}%"))
            )

    offset = (page - 1) * per_page
    results = query.order_by(PrSalary.SalaryMonth.desc()).offset(offset).limit(per_page).all()

    return [
        {
            "EmployeeID": salary.EmployeeID,
            "SalaryID": salary.SalaryID,
            "FullName": salary.employee.FullName,
            "SalaryMonth": salary.SalaryMonth,
            "BaseSalary": salary.BaseSalary,
            "Bonus": salary.Bonus,
            "Deductions": salary.Deductions,
            "NetSalary": salary.NetSalary,
            "Status": salary.employee.Status
        }
        for salary in results
    ]

def update_payroll(session: Session, payroll_id: int, update_data : PayrollUpdate):
    payroll_emp = session.query(PrSalary).filter_by(SalaryID=payroll_id).first()

    if not payroll_emp:
        raise HTTPException(status_code=404, detail=f"Salary ID không tồn tại trong: payroll")
    

    # chỉ cập nhật 2 trường là Bonus và Deductions từ đâu vào
    try:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(payroll_emp, field, value)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật trong payroll: {str(e)}")

    return {"message": f"Cập nhật bảng lương {payroll_id} thành công."}


def get_attendance_records(
        session: Session, 
        page: int = 1, 
        per_page: int = 10,
        search_date: Optional[date] = None, 
        employee_id: Optional[int] = None
        )-> List[PrAttendance]:
    query = session.query(PrAttendance).options(
        joinedload(PrAttendance.employee).joinedload(PrEmployee.department),
        joinedload(PrAttendance.employee).joinedload(PrEmployee.position)
    )

    if search_date:
        query = query.filter(
            extract('year', PrAttendance.AttendanceMonth) == search_date.year,
            extract('month', PrAttendance.AttendanceMonth) == search_date.month
        )

    if employee_id:
        query = query.filter(PrAttendance.EmployeeID == employee_id)

    offset = (page - 1) * per_page
    results = query.order_by(PrAttendance.AttendanceMonth.desc()).offset(offset).limit(per_page).all()

    return results

def get_personal_attendance(
        session: Session,
        employee_id: int
        )-> List[PrAttendance]:

    query = session.query(PrAttendance).filter(PrAttendance.EmployeeID == employee_id)

    if not query:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy dữ liệu về điểm danh của nhân viên {employee_id}")

    return query.all()


def get_personal_payroll(
        session: Session,
        employee_id: int
        )-> List[PrSalary]:
    query = session.query(PrSalary).filter(PrSalary.EmployeeID == employee_id)

    if not query:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy dữ liệu về bảng lương của nhân viên {employee_id}")

    return query.all()
