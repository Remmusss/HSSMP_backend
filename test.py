# create user script

from src.schemas.user import User
from src.databases.user_db import get_sync_db as get_sync_user_db
from sqlalchemy.orm import Session
from src.models.user import Role
from passlib.context import CryptContext

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def hash_password(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

if __name__ == "__main__":
    sdb = get_sync_user_db()
    for db in sdb:
        user = User(Employee_id=1, Username="admin", Password=hash_password("admin"), Role=Role.ADMIN.value)
        create_user(db, user)

        user = User(Employee_id=2, Username="hr_manager", Password=hash_password("hr_manager"), Role=Role.HR_MANAGER.value)
        create_user(db, user)

        user = User(Employee_id=3, Username="payroll_manager", Password=hash_password("payroll_manager"), Role=Role.PAYROLL_MANAGER.value)
        create_user(db, user)

        user = User(Employee_id=4, Username="employee", Password=hash_password("employee"), Role=Role.EMPLOYEE.value)
        create_user(db, user)


