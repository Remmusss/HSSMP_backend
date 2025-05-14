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
    Position as HmPosition
)
from ..schemas.payroll import (
    Department as PrDepartment,
    Employee as PrEmployee,
    Salary as PrSalary,
    Attendance as PrAttendance
)

from ..schemas.user import User

from src.utils.auth import get_current_user
from src.utils.employees import view_employee_details_logic
from src.utils.payroll import get_personal_payroll, get_personal_attendance

def read_profile_logic(db_user: Session, db_human: Session, db_payroll: Session, token: str):
    user = get_current_user(db_user, token)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực tài khoản",
        headers={"WWW-Authenticate": "Bearer"},
    )    

    if not user:
        raise credentials_exception

    try:
        employee = view_employee_details_logic(session=db_human, employee_id=user.Employee_id)
    
        if employee:
            payroll = get_personal_payroll(session=db_payroll, employee_id=user.Employee_id)
            attendance = get_personal_attendance(session=db_payroll, employee_id=user.Employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tìm kiếm nhân viên: {str(e)}")


    return {
        "username": user.Username,
        "employee_id": user.Employee_id,
        "role": user.Role,
        "employee_details": employee if employee else "Không tìm thấy dữ liệu về employee",
        "payroll_details": payroll if payroll else "Không tìm thấy dữ liệu về payroll",
        "attendance_details": attendance if attendance else "Không tìm thấy dữ liệu về attendance"
    }
