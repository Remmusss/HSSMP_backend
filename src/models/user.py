
from enum import Enum
from pydantic import BaseModel
class Role(Enum):
    ADMIN = "Admin"
    EMPLOYEE = "Employee"
    HR_MANAGER = "HR Manager"
    PAYROLL_MANAGER = "Payroll Manager"

class UserResponse(BaseModel):
    Username: str
    Role: Role
    Employee_id: int
