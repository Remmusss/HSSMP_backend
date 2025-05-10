from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


class DepartmentOut(BaseModel):
    DepartmentID: int
    DepartmentName: str

    class Config:
        orm_mode = True


class PositionOut(BaseModel):
    PositionID: int
    PositionName: str

    class Config:
        orm_mode = True


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
        orm_mode = True




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
    FullName: Optional[str] = None
    DateOfBirth: Optional[str] = None
    Gender: Optional[str] = None
    PhoneNumber: Optional[str] = None
    Email: Optional[EmailStr] = None
    HireDate: Optional[str] = None
    DepartmentID: Optional[int] = None
    PositionID: Optional[int] = None
    Status: Optional[str] = None