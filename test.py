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

from src.schemas.human import (
    Department as HmDepartment,
    Employee as HmEmployee,
    Dividend as HmDividend,
    Position as HmPosition,
)
from src.schemas.payroll import (
    Department as PrDepartment,
    Employee as PrEmployee,
    Salary as PrSalary,
    Attendance as PrAttendance,
)

from src.schemas.user import User
from src.utils.auth import get_current_user

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@company.com")

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
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Lỗi gửi email: {str(e)}")
        return False


def send_monthly_salary_notification(db_human: Session, db_payroll: Session, month: Optional[date] = None) -> Dict[str, Any]:
    """
    Gửi email thông báo lương hàng tháng cho nhân viên
    
    Args:
        db_human: Session database human
        db_payroll: Session database payroll
        month: Tháng muốn gửi thông báo lương, mặc định là tháng hiện tại
        
    Returns:
        Dict[str, Any]: Kết quả gửi email
    """
    if not month:
        month = datetime.today().date().replace(day=1)
    
    # Lấy tất cả lương của tháng
    salary_records = (
        db_payroll.query(PrSalary)
        .filter(
            extract("year", PrSalary.SalaryMonth) == month.year,
            extract("month", PrSalary.SalaryMonth) == month.month
        )
        .all()
    )
    
    if not salary_records:
        return {
            "success": False,
            "message": f"Không có dữ liệu lương cho tháng {month.month}/{month.year}",
            "sent_count": 0,
            "total_count": 0
        }
    
    # Lấy danh sách nhân viên để có email
    employee_ids = [salary.EmployeeID for salary in salary_records]
    employees = db_human.query(HmEmployee).filter(HmEmployee.EmployeeID.in_(employee_ids)).all()
    
    # Tạo map employee_id -> email
    employee_emails = {emp.EmployeeID: emp.Email for emp in employees if emp.Email}
    
    sent_count = 0
    failed_count = 0
    
    for salary in salary_records:
        employee_id = salary.EmployeeID
        
        if employee_id not in employee_emails:
            continue
            
        email = employee_emails[employee_id]
        
        # Lấy thông tin nhân viên
        employee = next((emp for emp in employees if emp.EmployeeID == employee_id), None)
        if not employee:
            continue
            
        # Lấy thông tin phòng ban
        department = db_human.query(HmDepartment).filter(HmDepartment.DepartmentID == employee.DepartmentID).first()
        department_name = department.DepartmentName if department else "Chưa phân bổ"
        
        # Lấy thông tin chức vụ
        position = db_human.query(HmPosition).filter(HmPosition.PositionID == employee.PositionID).first()
        position_name = position.PositionName if position else "Chưa phân bổ"
        
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
                            <td>{format(salary.BaseSalary, ',d')}</td>
                        </tr>
                        <tr>
                            <td>Phụ cấp</td>
                            <td>{format(salary.Allowance, ',d')}</td>
                        </tr>
                        <tr>
                            <td>Thưởng</td>
                            <td>{format(salary.Bonus, ',d')}</td>
                        </tr>
                        <tr>
                            <td>Khấu trừ</td>
                            <td>{format(salary.Deduction, ',d')}</td>
                        </tr>
                        <tr>
                            <td>Thuế</td>
                            <td>{format(salary.Tax, ',d')}</td>
                        </tr>
                        <tr>
                            <td><b>Lương thực lãnh</b></td>
                            <td><b>{format(salary.NetSalary, ',d')}</b></td>
                        </tr>
                    </table>
                    
                    <p>Lương đã được chuyển vào tài khoản của bạn. Nếu có bất kỳ thắc mắc nào về bảng lương, vui lòng liên hệ với phòng nhân sự.</p>
                    
                    <p>Trân trọng,<br>
                    Phòng Nhân sự</p>
                </div>
                <div class="footer">
                    <p>Đây là email tự động, vui lòng không trả lời email này.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Gửi email
        success = send_email(email, subject, html_body)
        
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    return {
        "success": True,
        "message": f"Đã gửi {sent_count} email thông báo lương tháng {month.month}/{month.year}",
        "sent_count": sent_count,
        "failed_count": failed_count,
        "total_count": len(salary_records)
    }


def format(value, format_str):
    """
    Định dạng số để hiển thị trong email
    """
    if value is None:
        return "0"
    return format_str.format(int(value))


from src.databases.human_db import get_sync_db as get_sync_human_db
from src.databases.payroll_db import get_sync_db as get_sync_payroll_db

if __name__ == "__main__":
    db_human = get_sync_human_db()
    db_payroll = get_sync_payroll_db()
    send_monthly_salary_notification(db_human, db_payroll, date(2025, 5, 1))
