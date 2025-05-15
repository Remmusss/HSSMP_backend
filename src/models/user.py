from enum import Enum
from pydantic import BaseModel
from typing import Optional

class Role(Enum):
    ADMIN = "Admin"
    EMPLOYEE = "Employee"
    HR_MANAGER = "HR Manager"
    PAYROLL_MANAGER = "Payroll Manager"

class UserResponse(BaseModel):
    Username: str
    Role: Role
    Employee_id: int


class UserCreate(BaseModel):
    Username: str
    Password: str
    Role: Role
    Employee_id: Optional[int] = None

class UserUpdate(BaseModel):
    Password: Optional[str] = None
    Role: Optional["Role"] = None
    Employee_id: Optional[int] = None
