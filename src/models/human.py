from pydantic import BaseModel, EmailStr
from datetime import date, datetime
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
    DateOfBirth: date
    Gender: Optional[str]
    PhoneNumber: Optional[str]
    Email: str
    HireDate: date
    Status: Optional[str]
    CreatedAt: datetime
    UpdatedAt: datetime
    Department: Optional[DepartmentOut]
    Position: Optional[PositionOut]

    class Config:
        from_attributes = True




class EmployeeCreate(BaseModel):
    EmployeeID: Optional[int] = None  
    FullName: str
    DateOfBirth: date
    Gender: Optional[str]
    PhoneNumber: Optional[str]
    Email: EmailStr
    HireDate: date
    DepartmentID: int
    PositionID: int
    Status: Optional[str] = "Active"


class EmployeeUpdate(BaseModel):
    DepartmentID: Optional[int] = None
    PositionID: Optional[int] = None
    Status: Optional[str] = None