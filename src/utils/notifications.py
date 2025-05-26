from sqlalchemy import func, desc, extract
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import concurrent.futures
from time import time

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
)

from ..schemas.user import User
from src.utils.auth import get_current_user

# Tải biến môi trường
load_dotenv()

# Cấu hình email
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@company.com")

# Số worker threads tối đa cho gửi email (tăng hoặc giảm dựa trên tài nguyên hệ thống)
MAX_WORKER_THREADS = 5


def upcoming_anniversaries(session: Session, window_days: int = 30):
    today = datetime.today().date()
    upcoming = []

    employees = session.query(HmEmployee).all()

    for emp in employees:
        if not emp.HireDate:
            continue

        hire_date = emp.HireDate

        for milestone in [1, 5, 10, 15, 20, 25, 30]:
            anniversary_date = hire_date.replace(year=hire_date.year + milestone)
            delta = (anniversary_date - today).days

            upcoming_milestone = milestone + 5 if milestone % 5 == 0 else 5

            if 0 <= delta <= window_days:
                upcoming.append(
                    {
                        "EmployeeID": emp.EmployeeID,
                        "FullName": emp.FullName,
                        "MilestoneYears": milestone,
                        "JoinDate": hire_date.strftime("%Y-%m-%d"),
                        "AnniversaryDate": anniversary_date.strftime("%Y-%m-%d"),
                        "UpcomingMilestone": upcoming_milestone,
                    }
                )
                break

    return {
        "count": len(upcoming),
        "upcoming_anniversaries": upcoming if upcoming else "Không có thông báo",
    }


def absent_days_warning(session: Session, windows_month: int = 3):
    today = datetime.today().date()
    warnings = []

    attendance = session.query(PrAttendance).all()

    for att in attendance:
        absent_days = att.AbsentDays
        leave_days = att.LeaveDays

        month_notification = today.month - att.AttendanceMonth.month

        if absent_days > leave_days and month_notification <= windows_month:
            warnings.append(
                {
                    "EmployeeID": att.EmployeeID,
                    "AllowedLeaveDays": leave_days,
                    "TakenLeaveDays": absent_days,
                    "ExcessDays": absent_days - leave_days,
                    "AttendanceMonth": att.AttendanceMonth.strftime("%Y-%m-%d"),
                }
            )

    return {
        "count": len(warnings),
        "absent_days_warning": warnings if warnings else "Không có thông báo",
    }


def absent_days_warning_personal(
    db_user: Session, db_payroll: Session, token: str, windows_month: int = 3
):
    user = get_current_user(db_user, token)

    credentials_exception = HTTPException(
        status_code=401,
        detail="Không thể xác thực tài khoản",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise credentials_exception

    today = datetime.today().date()
    warnings = []

    attendance = (
        db_payroll.query(PrAttendance)
        .filter(PrAttendance.EmployeeID == user.Employee_id)
        .all()
    )

    for att in attendance:
        absent_days = att.AbsentDays
        leave_days = att.LeaveDays

        month_notification = today.month - att.AttendanceMonth.month

        if absent_days > leave_days and month_notification <= windows_month:
            warnings.append(
                {
                    "EmployeeID": att.EmployeeID,
                    "AllowedLeaveDays": leave_days,
                    "TakenLeaveDays": absent_days,
                    "ExcessDays": absent_days - leave_days,
                    "AttendanceMonth": att.AttendanceMonth.strftime("%Y-%m-%d"),
                }
            )

    return {
        "count": len(warnings),
        "absent_days_warning": warnings if warnings else "Không có thông báo",
    }


def salary_gap_warning(session: Session, allowed_gap_percentage: int = 30):
    warnings = []

    employees = session.query(PrEmployee).options(joinedload(PrEmployee.salaries)).all()

    for employee in employees:
        salaries = (
            session.query(PrSalary)
            .filter(PrSalary.EmployeeID == employee.EmployeeID)
            .order_by(PrSalary.SalaryMonth.desc())
            .limit(2)
            .all()
        )

        if len(salaries) < 2:
            continue

        current_salary = salaries[0].NetSalary
        previous_salary = salaries[1].NetSalary

        if previous_salary or previous_salary > 0:
            gap_percentage = (current_salary - previous_salary) / previous_salary * 100

            if abs(gap_percentage) >= allowed_gap_percentage:
                warnings.append(
                    {
                        "EmployeeID": employee.EmployeeID,
                        "EmployeeName": employee.FullName,
                        "CurrentSalary": current_salary,
                        "PreviousSalary": previous_salary,
                        "GapPercentage": round(gap_percentage, 2),
                        "CurrentMonth": salaries[0].SalaryMonth.strftime("%Y-%m-%d"),
                        "PreviousMonth": salaries[1].SalaryMonth.strftime("%Y-%m-%d"),
                    }
                )

    return {
        "count": len(warnings),
        "salary_gap_warning": warnings if warnings else "Không có thông báo",
    }


def salary_gap_warning_personal(
    db_user: Session, db_payroll: Session, token: str, allowed_gap_percentage: int = 30
):
    user = get_current_user(db_user, token)

    credentials_exception = HTTPException(
        status_code=401,
        detail="Không thể xác thực tài khoản",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise credentials_exception

    warnings = []

    salaries = (
        db_payroll.query(PrSalary)
        .filter(PrSalary.EmployeeID == user.Employee_id)
        .order_by(PrSalary.SalaryMonth.desc())
        .limit(2)
        .all()
    )

    if len(salaries) < 2:
        return {"salary_gap_warning": "Không có thông báo"}

    current_salary = salaries[0].NetSalary
    previous_salary = salaries[1].NetSalary

    gap_percentage = (current_salary - previous_salary) / previous_salary * 100

    if abs(gap_percentage) >= allowed_gap_percentage:
        employee = (
            db_payroll.query(PrEmployee)
            .filter(PrEmployee.EmployeeID == user.Employee_id)
            .first()
        )
        employee_name = employee.FullName if employee else user.FullName

        warnings.append(
            {
                "EmployeeID": user.Employee_id,
                "EmployeeName": employee_name,
                "CurrentSalary": current_salary,
                "PreviousSalary": previous_salary,
                "GapPercentage": round(gap_percentage, 2),
                "CurrentMonth": salaries[0].SalaryMonth.strftime("%Y-%m-%d"),
                "PreviousMonth": salaries[1].SalaryMonth.strftime("%Y-%m-%d"),
            }
        )

    return {
        "count": len(warnings),
        "salary_gap_warning": warnings if warnings else "Không có thông báo",
    }


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Gửi email sử dụng SMTP
    
    Args:
        to_email: Địa chỉ email người nhận
        subject: Tiêu đề email
        body_html: Nội dung email dạng HTML
        
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại
    """
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body_html, 'html'))
        
        print(f"Kết nối tới máy chủ SMTP: {EMAIL_HOST}:{EMAIL_PORT}")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.set_debuglevel(0)  # Bật chế độ debug để xem các thông báo lỗi
        
        server.starttls()
        
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        server.send_message(msg)
        
        server.quit()
        
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi gửi email: {str(e)}")
        return False


def send_email_task(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hàm gửi email riêng lẻ, được sử dụng bởi ThreadPoolExecutor
    """
    try:
        to_email = email_data.get("to_email")
        subject = email_data.get("subject")
        body_html = email_data.get("body_html")
        employee_id = email_data.get("employee_id")
        
        success = send_email(to_email, subject, body_html)
        
        return {
            "employee_id": employee_id,
            "email": to_email,
            "success": success
        }
    except Exception as e:
        return {
            "employee_id": email_data.get("employee_id"),
            "email": email_data.get("to_email"),
            "success": False,
            "error": str(e)
        }


def send_monthly_salary_notification(db_human: Session, db_payroll: Session, month_str: Optional[str] = None) -> Dict[str, Any]:
    start_time = time()
    
    try:
        if month_str:
            if len(month_str.split("-")) == 2:
                month_str += "-01"  # Thêm ngày đầu tháng nếu chỉ có YYYY-MM
            month = datetime.strptime(month_str, "%Y-%m-%d").date()
        else:
            month = datetime.today().date().replace(day=1)
            
        print(f"Chuẩn bị gửi thông báo lương tháng {month.month}/{month.year}")
        
        query = (
            db_payroll.query(PrSalary)
            .filter(
                extract("year", PrSalary.SalaryMonth) == month.year,
                extract("month", PrSalary.SalaryMonth) == month.month
            )
        )
        
        latest_salary_subq = (
            db_payroll.query(
                PrSalary.EmployeeID,
                func.max(PrSalary.SalaryID).label("max_salary_id")
            )
            .filter(
                extract("year", PrSalary.SalaryMonth) == month.year,
                extract("month", PrSalary.SalaryMonth) == month.month
            )
            .group_by(PrSalary.EmployeeID)
            .subquery()
        )
        
        salary_records = (
            db_payroll.query(PrSalary)
            .join(
                latest_salary_subq,
                (PrSalary.EmployeeID == latest_salary_subq.c.EmployeeID) &
                (PrSalary.SalaryID == latest_salary_subq.c.max_salary_id)
            )
            .all()
        )
        
        
        if not salary_records:
            return {
                "message": f"Không có dữ liệu lương cho tháng {month.month}/{month.year}",
                "sent_count": 0,
                "total_count": 0,
                "time_taken": time() - start_time
            }
        
        # Lấy danh sách ID nhân viên
        employee_ids = [salary.EmployeeID for salary in salary_records]
        
        # Lấy tất cả dữ liệu cần thiết trong một lần truy vấn
        employees = db_human.query(HmEmployee).filter(HmEmployee.EmployeeID.in_(employee_ids)).all()
        departments = db_human.query(HmDepartment).all()
        positions = db_human.query(HmPosition).all()

        query_time = time() - start_time
        print(f"Thời gian truy vấn SQL: {query_time:.2f} giây")
        
        # Tạo dictionaries để truy cập nhanh
        employee_map = {emp.EmployeeID: emp for emp in employees}
        department_map = {d.DepartmentID: d.DepartmentName for d in departments}
        position_map = {p.PositionID: p.PositionName for p in positions}
        
        # Lọc những nhân viên có email
        employee_emails = {emp.EmployeeID: emp.Email for emp in employees if emp.Email}
        
        # Chuẩn bị danh sách công việc gửi email
        email_tasks = []
        
        for salary in salary_records:
            employee_id = salary.EmployeeID
            
            if employee_id not in employee_emails:
                continue
                
            email = employee_emails[employee_id]
            employee = employee_map.get(employee_id)
            
            if not employee:
                continue
                
            # Lấy thông tin phòng ban và chức vụ
            department_name = department_map.get(employee.DepartmentID, "Chưa phân bổ")
            position_name = position_map.get(employee.PositionID, "Chưa phân bổ")
            
            # Tạo nội dung email
            subject = f"Thông báo lương tháng {month.month}/{month.year}"
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                    }}
                    .container {{
                        width: 100%;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }}
                    .header {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                    }}
                    table, th, td {{
                        border: 1px solid #ddd;
                    }}
                    th, td {{
                        padding: 10px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    .footer {{
                        background-color: #f2f2f2;
                        padding: 10px;
                        text-align: center;
                        border-radius: 0 0 5px 5px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Thông báo lương tháng {month.month}/{month.year}</h2>
                    </div>
                    <div class="content">
                        <p>Kính gửi <b>{employee.FullName}</b>,</p>
                        
                        <p>Công ty trân trọng thông báo lương tháng {month.month}/{month.year} của bạn như sau:</p>
                        
                        <table>
                            <tr>
                                <th>Thông tin</th>
                                <th>Chi tiết</th>
                            </tr>
                            <tr>
                                <td>Mã nhân viên</td>
                                <td>{employee.EmployeeID}</td>
                            </tr>
                            <tr>
                                <td>Họ và tên</td>
                                <td>{employee.FullName}</td>
                            </tr>
                            <tr>
                                <td>Phòng ban</td>
                                <td>{department_name}</td>
                            </tr>
                            <tr>
                                <td>Chức vụ</td>
                                <td>{position_name}</td>
                            </tr>
                        </table>
                        
                        <table>
                            <tr>
                                <th>Mục lương</th>
                                <th>Giá trị (VNĐ)</th>
                            </tr>
                            <tr>
                                <td>Lương cơ bản</td>
                                <td>{format(salary.BaseSalary, ' VNĐ')}</td>
                            </tr>
                            <tr>
                                <td>Thưởng</td>
                                <td>{format(salary.Bonus, ' VNĐ')}</td>
                            </tr>
                            <tr>
                                <td>Khấu trừ</td>
                                <td>{format(salary.Deductions, ' VNĐ')}</td>
                            </tr>
                            <tr>
                                <td><b>Lương thực lãnh</b></td>
                                <td><b>{format(salary.NetSalary, ' VNĐ')}</b></td>
                            </tr>
                        </table>
                        
                        <p>Lương sẽ được chuyển vào tài khoản của bạn. Nếu có bất kỳ thắc mắc nào về bảng lương, vui lòng liên hệ với phòng kế toán.</p>
                        
                        <p>Trân trọng,<br>
                        Phòng Kế Toán</p>
                    </div>
                    <div class="footer">
                        <p>Đây là email tự động, vui lòng không trả lời email này.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Thêm công việc vào danh sách
            email_tasks.append({
                "employee_id": employee_id,
                "to_email": email,
                "subject": subject,
                "body_html": html_body
            })
        
        # Không có email nào để gửi
        if not email_tasks:
            return {
                "message": f"Không có email hợp lệ để gửi thông báo lương tháng {month.month}/{month.year}",
                "sent_count": 0,
                "total_count": 0,
                "time_taken": time() - start_time
            }
        
        prep_time = time() - start_time
        print(f"Thời gian chuẩn bị dữ liệu: {prep_time:.2f} giây")
        
        # Số lượng worker tối đa là MAX_WORKER_THREADS hoặc số lượng email, tùy theo giá trị nào nhỏ hơn
        worker_count = min(MAX_WORKER_THREADS, len(email_tasks))
        
        # Gửi email song song
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(send_email_task, task) for task in email_tasks]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        sent_count = sum(1 for r in results if r.get("success", False))
        failed_count = len(results) - sent_count
        emails_sent = [r.get("email") for r in results if r.get("success", False)]
        
        total_time = time() - start_time
        print(f"Hoàn thành gửi email trong {total_time:.2f} giây")
        
        return {
            "message": f"Đã gửi {sent_count}/{len(email_tasks)} email thông báo lương tháng {month.month}/{month.year}",
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_count": len(email_tasks),
            "emails": emails_sent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gửi email: {str(e)}")


def format(value, suffix):
    if value is None:
        return "0" + suffix
    
    amount = int(value)
    formatted = "{:,}".format(amount).replace(",", ".")
    
    return formatted + suffix
