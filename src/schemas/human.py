from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, Numeric, DateTime,
    text, NVARCHAR
)
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class Department(Base):
    __tablename__ = "Departments"

    DepartmentID = Column(Integer, primary_key=True, autoincrement=True)
    DepartmentName = Column(String(100), nullable=False)
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))
    UpdatedAt = Column(DateTime, server_default=text("GETDATE()"))

    employees = relationship("Employee", back_populates="department")


class Position(Base):
    __tablename__ = "Positions"

    PositionID = Column(Integer, primary_key=True, autoincrement=True)
    PositionName = Column(String(100), nullable=False)
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))
    UpdatedAt = Column(DateTime, server_default=text("GETDATE()"))

    employees = relationship("Employee", back_populates="position")


class Employee(Base):
    __tablename__ = "Employees"

    EmployeeID = Column(Integer, primary_key=True, autoincrement=True)
    FullName = Column(NVARCHAR(100), nullable=False)
    DateOfBirth = Column(Date, nullable=False)
    Gender = Column(NVARCHAR(10))
    PhoneNumber = Column(NVARCHAR(15))
    Email = Column(NVARCHAR(100), unique=True, nullable=False)
    HireDate = Column(Date, nullable=False)
    DepartmentID = Column(Integer, ForeignKey("Departments.DepartmentID"))
    PositionID = Column(Integer, ForeignKey("Positions.PositionID"))
    Status = Column(NVARCHAR(50))
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))
    UpdatedAt = Column(DateTime, server_default=text("GETDATE()"))

    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    dividends = relationship("Dividend", back_populates="employee")


class Dividend(Base):
    __tablename__ = "Dividends"

    DividendID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeID = Column(Integer, ForeignKey("Employees.EmployeeID"))
    DividendAmount = Column(Numeric(12, 2), nullable=False)
    DividendDate = Column(Date, nullable=False)
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))

    employee = relationship("Employee", back_populates="dividends")