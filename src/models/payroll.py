from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class DepartmentOut(BaseModel):
    DepartmentID: int
    DepartmentName: str

    class Config:
        from_attributes = True


class PositionOut(BaseModel):
    PositionID: int
    PositionName: str

    class Config:
        from_attributes = True


class EmployeeOut(BaseModel):
    EmployeeID: int
    FullName: str
    Department: Optional[DepartmentOut]
    Position: Optional[PositionOut]
    Status: Optional[str]

    class Config:
        from_attributes = True


class SalaryOut(BaseModel):
    SalaryID: int
    EmployeeID: int
    SalaryMonth: date
    BaseSalary: Decimal
    Bonus: Decimal
    Deductions: Decimal
    NetSalary: Decimal
    CreatedAt: datetime
    Employee: EmployeeOut

    class Config:
        from_attributes = True




class SalaryReportByDepartment(BaseModel):
    DepartmentID: int
    DepartmentName: str
    TotalSalary: Decimal
    AverageSalary: Decimal


class AttendanceWarning(BaseModel):
    EmployeeID: int
    FullName: str
    Department: Optional[str]
    Position: Optional[str]
    AttendanceMonth: date
    AbsentDays: int
    LeaveDays: int
    TotalLeave: int
    MaxAllowedLeave: int


class SalaryDifferenceWarning(BaseModel):
    EmployeeID: int
    FullName: str
    Department: Optional[str]
    Position: Optional[str]
    PreviousMonth: date
    CurrentMonth: date
    PreviousSalary: Decimal
    CurrentSalary: Decimal
    Difference: Decimal
    PercentageChange: float
    ThresholdPercent: float

class PayrollUpdate(BaseModel):
    Bonus: Optional[Decimal]
    Deductions: Optional[Decimal]
