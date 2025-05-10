from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, DECIMAL, DateTime, func
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'

    DepartmentID = Column(Integer, primary_key=True)
    DepartmentName = Column(String(100), nullable=False)

    employees = relationship("Employee", back_populates="department")


class Position(Base):
    __tablename__ = 'positions'

    PositionID = Column(Integer, primary_key=True)
    PositionName = Column(String(100), nullable=False)

    employees = relationship("Employee", back_populates="position")


class Employee(Base):
    __tablename__ = 'employees'

    EmployeeID = Column(Integer, primary_key=True)
    FullName = Column(String(100), nullable=False)
    DepartmentID = Column(Integer, ForeignKey('departments.DepartmentID'))
    PositionID = Column(Integer, ForeignKey('positions.PositionID'))
    Status = Column(String(50), nullable=True)

    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    attendances = relationship("Attendance", back_populates="employee")
    salaries = relationship("Salary", back_populates="employee")


class Attendance(Base):
    __tablename__ = 'attendance'

    AttendanceID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey('employees.EmployeeID'))
    WorkDays = Column(Integer, nullable=False)
    AbsentDays = Column(Integer, default=0)
    LeaveDays = Column(Integer, default=0)
    AttendanceMonth = Column(Date, nullable=False)
    CreatedAt = Column(DateTime, server_default=func.now())

    employee = relationship("Employee", back_populates="attendances")


class Salary(Base):
    __tablename__ = 'salaries'

    SalaryID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey('employees.EmployeeID'))
    SalaryMonth = Column(Date, nullable=False)
    BaseSalary = Column(DECIMAL(12, 2), nullable=False)
    Bonus = Column(DECIMAL(12, 2), default=0.00)
    Deductions = Column(DECIMAL(12, 2), default=0.00)
    NetSalary = Column(DECIMAL(12, 2), nullable=False)
    CreatedAt = Column(DateTime, server_default=func.now())

    employee = relationship("Employee", back_populates="salaries")