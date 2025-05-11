from sqlalchemy import delete, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select

from fastapi import HTTPException

from typing import Optional, List
from datetime import date, datetime, timedelta

from ..models.human import DepartmentCreate, DepartmentUpdate

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

def add_and_sync_department(session_human: Session, session_payroll: Session, department: DepartmentCreate):
    if department.DepartmentID is not None:
        exists_human = session_human.query(HmDepartment).filter_by(DepartmentID=department.DepartmentID).first()
        exists_payroll = session_payroll.query(PrDepartment).filter_by(DepartmentID=department.DepartmentID).first()

        if exists_human or exists_payroll:
            source = []
            if exists_human:
                source.append("HUMAN_2025")
            if exists_payroll:
                source.append("payroll")
            raise HTTPException(status_code=400, detail=f"DepartmentID đã tồn tại trong: {', '.join(source)}")
    else:
        max_id_human = session_human.query(HmDepartment.DepartmentID).order_by(HmDepartment.DepartmentID.desc()).first()
        max_id_payroll = session_payroll.query(PrDepartment.DepartmentID).order_by(PrDepartment.DepartmentID.desc()).first()

        max_id = max(
            max_id_human[0] if max_id_human else 0,
            max_id_payroll[0] if max_id_payroll else 0
        )
        department.DepartmentID = max_id + 1

        if session_human.query(HmDepartment).filter_by(DepartmentID=department.DepartmentID).first():
            raise HTTPException(status_code=400, detail="DepartmentID đã tồn tại trong HUMAN_2025")
        if session_payroll.query(PrDepartment).filter_by(DepartmentID=department.DepartmentID).first():
            raise HTTPException(status_code=400, detail="DepartmentID đã tồn tại trong payroll")
        
        try:
            new_human_dept = HmDepartment(
                DepartmentID=department.DepartmentID,
                DepartmentName=department.DepartmentName,
                CreatedAt=department.CreatedAt,
                UpdatedAt=department.UpdatedAt
            )
            session_human.add(new_human_dept)
            session_human.commit()

            new_payroll_dept = PrDepartment(
                DepartmentID=department.DepartmentID,
                DepartmentName=department.DepartmentName,
            )
            session_payroll.add(new_payroll_dept)
            session_payroll.commit()

            return {"message": "Phòng ban đã được thêm và đồng bộ thành công.", "DepartmentID": department.DepartmentID}
        except Exception as e:
            session_human.rollback()
            session_payroll.rollback()
            raise HTTPException(status_code=500, detail=f"Lỗi khi thêm phòng ban: {str(e)}")    



def update_and_sync_department(session_human: Session, session_payroll: Session, department_id: int, department: DepartmentUpdate):
    human_dept = session_human.query(HmDepartment).filter_by(DepartmentID=department_id).first()
    payroll_dept = session_payroll.query(PrDepartment).filter_by(DepartmentID=department_id).first()

    if not human_dept or not payroll_dept:
        missing = []
        if not human_dept:
            missing.append("HUMAN_2025")
        if not payroll_dept:
            missing.append("payroll")
        raise HTTPException(status_code=404, detail=f"Phòng ban không tồn tại trong: {', '.join(missing)}")
    
    try:
        for field, value in department.model_dump(exclude_unset=True).items():
            setattr(human_dept, field, value)
        session_human.commit()
    except Exception as e:
        session_human.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật trong HUMAN_2025: {str(e)}")
    
    try:
        for field in ['DepartmentName', 'UpdatedAt']:
            if field in department.model_dump(exclude_unset=True):
                setattr(payroll_dept, field, getattr(human_dept, field))
        session_payroll.commit()
    except Exception as e:
        session_payroll.rollback()
        session_human.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật trong payroll: {str(e)}")
    
    return {"message": "Phòng ban đã được cập nhật và đồng bộ thành công.", "DepartmentID": department_id}


def delete_and_sync_department(session_human: Session, session_payroll: Session, department_id: int):
    human_dept = session_human.query(HmDepartment).filter_by(DepartmentID=department_id).first()
    payroll_dept = session_payroll.query(PrDepartment).filter_by(DepartmentID=department_id).first()

    if not human_dept or not payroll_dept:
        missing = []
        if not human_dept:
            missing.append("HUMAN_2025")
        if not payroll_dept:
            missing.append("payroll")
        raise HTTPException(status_code=404, detail=f"Phòng ban không tồn tại trong: {', '.join(missing)}")
    
    try:
        human_employees = session_human.query(HmEmployee).filter_by(DepartmentID=department_id).all()
        payroll_employees = session_payroll.query(PrEmployee).filter_by(DepartmentID=department_id).all()

        if human_dept:
            session_human.delete(human_dept)
        
        if payroll_dept:
            session_payroll.delete(payroll_dept)
        

        for emp in human_employees:
            emp.DepartmentID = None
        
        for emp in payroll_employees:
            emp.DepartmentID = None

        session_human.commit()
        session_payroll.commit()

        affected_employees = max(len(human_employees), len(payroll_employees))
        message = "Phòng ban đã được xóa thành công khỏi cả hai hệ thống."
        if affected_employees > 0:
            message += f" Đã cập nhật {affected_employees} nhân viên sang không có phòng ban."

        return {"message": message, "affected_employees": affected_employees}

    except Exception as e:
        session_human.rollback()
        session_payroll.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa phòng ban: {str(e)}")
