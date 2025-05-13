from sqlalchemy import delete, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select

from fastapi import HTTPException

from typing import Optional, List
from datetime import date, datetime, timedelta

from src.models.human import PositionCreate, PositionUpdate

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


def read_positions(session: Session):
    employee_count_subquery = (
        session.query(
            HmEmployee.PositionID,
            func.count(HmEmployee.EmployeeID).label("employee_count"),
        )
        .group_by(HmEmployee.PositionID)
        .subquery()
    )

    query = session.query(
        HmPosition,
        func.coalesce(employee_count_subquery.c.employee_count, 0).label(
            "employee_count"
        ),
    ).outerjoin(
        employee_count_subquery,
        HmPosition.PositionID == employee_count_subquery.c.PositionID,
    )

    results = query.order_by(HmPosition.PositionID).all()

    return [
        {
            "PositionID": position.PositionID,
            "PositionName": position.PositionName,
            "TotalEmployees": employee_count,
            "CreatedAt": position.CreatedAt,
            "UpdatedAt": position.UpdatedAt,
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
            func.count(HmEmployee.EmployeeID).label("employee_count"),
        )
        .join(HmEmployee, HmDepartment.DepartmentID == HmEmployee.DepartmentID)
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
                "EmployeeCount": emp_count,
            }
            for dept_id, dept_name, emp_count in results
        ],
    }


def add_and_sync_position(
    session_human: Session, session_payroll: Session, position: PositionCreate
):
    max_id_human = (
        session_human.query(HmPosition.PositionID)
        .order_by(HmPosition.PositionID.desc())
        .first()
    )
    max_id_payroll = (
        session_payroll.query(PrPosition.PositionID)
        .order_by(PrPosition.PositionID.desc())
        .first()
    )

    max_id = max(
        max_id_human[0] if max_id_human else 0,
        max_id_payroll[0] if max_id_payroll else 0,
    )

    position_id = max_id + 1

    if session_human.query(HmPosition).filter_by(PositionID=position_id).first():
        raise HTTPException(
            status_code=400, detail="PositionID đã tồn tại trong HUMAN_2025"
        )
    if session_payroll.query(PrPosition).filter_by(PositionID=position_id).first():
        raise HTTPException(
            status_code=400, detail="PositionID đã tồn tại trong payroll"
        )

    try:
        new_human_position = HmPosition(
            PositionID=position_id,
            PositionName=position.PositionName,
            CreatedAt=position.CreatedAt,
            UpdatedAt=position.UpdatedAt,
        )
        session_human.add(new_human_position)
        session_human.commit()

        new_payroll_position = PrPosition(
            PositionID=position_id,
            PositionName=position.PositionName,
        )
        session_payroll.add(new_payroll_position)
        session_payroll.commit()

        return {
            "message": "Chức vụ đã được thêm và đồng bộ hóa thành công",
            "PositionID": position_id,
        }

    except Exception as e:
        session_human.rollback()
        session_payroll.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm chức vụ: {str(e)}")


def update_and_sync_position(
    session_human: Session,
    session_payroll: Session,
    position_id: int,
    position: PositionUpdate,
):
    human_position = (
        session_human.query(HmPosition).filter_by(PositionID=position_id).first()
    )
    payroll_position = (
        session_payroll.query(PrPosition).filter_by(PositionID=position_id).first()
    )

    if not human_position or not payroll_position:
        missing = []
        if not human_position:
            missing.append("HUMAN_2025")
        if not payroll_position:
            missing.append("payroll")
        raise HTTPException(
            status_code=404, detail=f"Chức vụ không tồn tại trong: {', '.join(missing)}"
        )

    try:
        for field, value in position.model_dump(exclude_unset=True).items():
            setattr(human_position, field, value)
        session_human.commit()
    except Exception as e:
        session_human.rollback()
        raise HTTPException(
            status_code=500, detail=f"Lỗi cập nhật trong HUMAN_2025: {str(e)}"
        )

    try:
        for field in ["PositionName", "UpdatedAt"]:
            setattr(payroll_position, field, getattr(human_position, field))
        session_payroll.commit()
    except Exception as e:
        session_payroll.rollback()
        raise HTTPException(
            status_code=500, detail=f"Lỗi cập nhật trong payroll: {str(e)}"
        )

    return {
        "message": "Chức vụ đã được cập nhật và đồng bộ hóa thành công",
        "PositionID": position_id,
    }


def delete_and_sync_position(
    session_human: Session, session_payroll: Session, position_id: int
):
    human_position = (
        session_human.query(HmPosition).filter_by(PositionID=position_id).first()
    )
    payroll_position = (
        session_payroll.query(PrPosition).filter_by(PositionID=position_id).first()
    )

    if not human_position or not payroll_position:
        missing = []
        if not human_position:
            missing.append("HUMAN_2025")
        if not payroll_position:
            missing.append("payroll")
        raise HTTPException(
            status_code=404, detail=f"Chức vụ không tồn tại trong: {', '.join(missing)}"
        )

    try:
        human_employees = (
            session_human.query(HmEmployee).filter_by(PositionID=position_id).all()
        )
        payroll_employees = (
            session_payroll.query(PrEmployee).filter_by(PositionID=position_id).all()
        )

        if human_employees or payroll_employees:
            employee_info = {}

            for emp in human_employees:
                employee_info[emp.EmployeeID] = {
                    "EmployeeID": emp.EmployeeID,
                    "FullName": emp.FullName,
                    "Source": "HUMAN_2025",
                }

            for emp in payroll_employees:
                if emp.EmployeeID in employee_info:
                    employee_info[emp.EmployeeID]["Source"] += ", payroll"
                else:
                    employee_info[emp.EmployeeID] = {
                        "EmployeeID": emp.EmployeeID,
                        "FullName": emp.FullName,
                        "Source": "payroll",
                    }

            employee_list = sorted(
                employee_info.values(), key=lambda x: x["EmployeeID"]
            )

            error_message = f"Không thể xóa vị trí. Có {len(employee_list)} nhân viên thuộc vị trí này."
            raise HTTPException(
                status_code=400,
                detail={"message": error_message, "employees": employee_list},
            )

        if human_position:
            session_human.delete(human_position)

        if payroll_position:
            session_payroll.delete(payroll_position)

        session_human.commit()
        session_payroll.commit()

        return {
            "message": f"Chức vụ {position_id} đã được xóa thành công khỏi cả hai hệ thống.",
            "position_name": human_position.PositionName
        }

    except HTTPException:
        raise
    except Exception as e:
        session_human.rollback()
        session_payroll.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa chức vụ: {str(e)}")
