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

from ..models.human import (
    EmployeeCreate,
    EmployeeUpdate
)



def get_employees(session: Session, page: int = 1, per_page: int = 10) -> List[HmEmployee]:
    query = session.query(HmEmployee).options(
        joinedload(HmEmployee.department), joinedload(HmEmployee.position)
    )

    offset = (page - 1) * per_page

    results = query.order_by(HmEmployee.EmployeeID).offset(offset).limit(per_page).all()

    return results



def search_employees_logic(
    session: Session,
    search_query: str = None,
    page: int = 1,
    per_page: int = 10
):
    query = session.query(HmEmployee).join(
        HmDepartment, HmEmployee.DepartmentID == HmDepartment.DepartmentID, isouter=True
    )
    
    query = query.join(
        HmPosition, HmEmployee.PositionID == HmPosition.PositionID, isouter=True
    )

    if search_query:
        try:
            numeric_query = int(search_query)
            query = query.filter(
                (HmEmployee.EmployeeID == numeric_query) |
                (HmEmployee.FullName.ilike(f"%{search_query}%")) |
                (HmDepartment.DepartmentName.ilike(f"%{search_query}%")) |
                (HmPosition.PositionName.ilike(f"%{search_query}%"))
            )
        except ValueError:
            query = query.filter(
                (HmEmployee.FullName.ilike(f"%{search_query}%")) |
                (HmDepartment.DepartmentName.ilike(f"%{search_query}%")) |
                (HmPosition.PositionName.ilike(f"%{search_query}%"))
            )

    offset = (page - 1) * per_page
    results = query.order_by(HmEmployee.EmployeeID).offset(offset).limit(per_page).all()

    return results



def add_and_sync_employee(session_human: Session, session_payroll: Session, employee: EmployeeCreate):
    if employee.EmployeeID is not None:
        exists_human = session_human.query(HmEmployee).filter_by(EmployeeID=employee.EmployeeID).first()
        exists_payroll = session_payroll.query(PrEmployee).filter_by(EmployeeID=employee.EmployeeID).first()

        if exists_human or exists_payroll:
            source = []
            if exists_human:
                source.append("HUMAN_2025")
            if exists_payroll:
                source.append("payroll")
            raise HTTPException(status_code=400, detail=f"EmployeeID đã tồn tại trong: {', '.join(source)}")
    else:
        max_id_human = session_human.query(HmEmployee.EmployeeID).order_by(HmEmployee.EmployeeID.desc()).first()
        max_id_payroll = session_payroll.query(PrEmployee.EmployeeID).order_by(PrEmployee.EmployeeID.desc()).first()

        max_id = max(
            max_id_human[0] if max_id_human else 0,
            max_id_payroll[0] if max_id_payroll else 0
        )
        employee.EmployeeID = max_id + 1

    if session_human.query(HmEmployee).filter_by(EmployeeID=employee.EmployeeID).first():
        raise HTTPException(status_code=400, detail="EmployeeID đã tồn tại trong HUMAN_2025")
    if session_payroll.query(PrEmployee).filter_by(EmployeeID=employee.EmployeeID).first():
        raise HTTPException(status_code=400, detail="EmployeeID đã tồn tại trong payroll")

    try:
        new_human_emp = HmEmployee(
            EmployeeID=employee.EmployeeID,
            FullName=employee.FullName,
            DateOfBirth=employee.DateOfBirth,
            Gender=employee.Gender,
            PhoneNumber=employee.PhoneNumber,
            Email=employee.Email,
            HireDate=employee.HireDate,
            DepartmentID=employee.DepartmentID,
            PositionID=employee.PositionID,
            Status=employee.Status
        )
        session_human.add(new_human_emp)
        session_human.commit()

        new_payroll_emp = PrEmployee(
            EmployeeID=employee.EmployeeID,
            FullName=employee.FullName,
            DepartmentID=employee.DepartmentID,
            PositionID=employee.PositionID,
            Status=employee.Status
        )
        session_payroll.add(new_payroll_emp)
        session_payroll.commit()

        return {"message": "Nhân viên đã được thêm và đồng bộ thành công.", "EmployeeID": employee.EmployeeID}

    except Exception as e:
        session_human.rollback()
        session_payroll.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm nhân viên: {str(e)}")    
    

def update_and_sync_employee(session_human : Session, session_payroll : Session, employee_id : int, update_data : EmployeeUpdate):
    human_emp = session_human.query(HmEmployee).filter_by(EmployeeID=employee_id).first()
    payroll_emp = session_payroll.query(PrEmployee).filter_by(EmployeeID=employee_id).first()

    if not human_emp or not payroll_emp:
        missing = []
        if not human_emp:
            missing.append("HUMAN_2025")
        if not payroll_emp:
            missing.append("payroll")
        raise HTTPException(status_code=404, detail=f"Nhân viên không tồn tại trong: {', '.join(missing)}")

    try:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(human_emp, field, value)
        session_human.commit()
    except Exception as e:
        session_human.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật trong HUMAN_2025: {str(e)}")

    try:
        #  chỉ cập nhật 3 trường là DepartmentID, PositionID, Status
        for field in ['DepartmentID', 'PositionID', 'Status']:
            if field in update_data.model_dump(exclude_unset=True):
                setattr(payroll_emp, field, getattr(human_emp, field))
        session_payroll.commit()
    except Exception as e:
        session_payroll.rollback()
        session_human.rollback()  
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật trong payroll: {str(e)}")

    return {"message": "Cập nhật và đồng bộ nhân viên thành công."}


def delete_employee_logic(session_human : Session, session_payroll: Session, employee_id: int):
    human_emp = session_human.query(HmEmployee).filter_by(EmployeeID=employee_id).first()
    payroll_emp = session_payroll.query(PrEmployee).filter_by(EmployeeID=employee_id).first()

    if not human_emp and not payroll_emp:
        raise HTTPException(status_code=404, detail="Nhân viên không tồn tại trong cả hai hệ thống.")

    if human_emp:
        dividend_exists = session_human.query(HmDividend).filter_by(EmployeeID=employee_id).first()
        if dividend_exists:
            raise HTTPException(
                status_code=400,
                detail="Không thể xóa. Nhân viên có dữ liệu cổ tức trong HUMAN_2025."
            )

    if payroll_emp:
        salary_exists = session_payroll.query(PrSalary).filter_by(EmployeeID=employee_id).first()
        attendance_exists = session_payroll.query(PrAttendance).filter_by(EmployeeID=employee_id).first()

        if salary_exists or attendance_exists:
            raise HTTPException(
                status_code=400,
                detail="Không thể xóa. Nhân viên có dữ liệu lương hoặc chấm công trong payroll."
            )

    try:
        if human_emp:
            session_human.delete(human_emp)
            session_human.commit()

        if payroll_emp:
            session_payroll.delete(payroll_emp)
            session_payroll.commit()

        return {"message": "Nhân viên đã được xóa thành công khỏi cả hai hệ thống."}

    except Exception as e:
        session_human.rollback()
        session_payroll.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa nhân viên: {str(e)}")
    

def view_employee_details_logic(session: Session, employee_id: int):
    employee = session.query(HmEmployee).options(
        joinedload(HmEmployee.department),
        joinedload(HmEmployee.position)
    ).filter(HmEmployee.EmployeeID == employee_id).first()
    
    return {
        "EmployeeID": employee.EmployeeID,
        "FullName": employee.FullName,
        "DateOfBirth": employee.DateOfBirth,
        "Gender": employee.Gender,
        "PhoneNumber": employee.PhoneNumber,
        "Email": employee.Email,
        "HireDate": employee.HireDate,
        "DepartmentID": employee.DepartmentID,
        "DepartmentName": employee.department.DepartmentName if employee.department else None,
        "PositionID": employee.PositionID,
        "PositionName": employee.position.PositionName if employee.position else None,
        "Status": employee.Status
    }

