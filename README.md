# HSSMP Backend

Backend service for ZENHRM SYSTEM MANAGEMENT PROJECT (HSSMP) - Dự án tích hợp hệ thống quản lý nhân sự.

## Chức năng

- Tích hợp dữ liệu giữa hai cơ sở dữ liệu: HUMAN_2025 (SQL Server) và payroll (MySQL)
- Quản lý nhân viên: thêm, sửa, xóa, tìm kiếm và đồng bộ dữ liệu giữa hai hệ thống
- API cho các thao tác quản lý nhân sự

## Yêu cầu

- Python 3.12+
- MySQL
- SQL Server (Microsoft)

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/Remmusss/HSSMP_backend.git
cd HSSMP_backend
```

### 2. Tạo môi trường ảo

```bash
python -m venv env
```

### 3. Kích hoạt môi trường ảo

Trên Windows:
```bash
env\Scripts\activate
```

Trên macOS/Linux:
```bash
source env/bin/activate
```

### 4. Cài đặt các thư viện

```bash
pip install -r requirements.txt
```

### 5. Tạo file `.env`

Tạo file `.env` trong thư mục gốc với nội dung sau:

```
# MySQL configuration (payroll)
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=payroll

# SQL Server configuration (HUMAN_2025)
SQLSERVER_HOST=localhost
SQLSERVER_DATABASE=HUMAN_2025

# DB cho accounts
SQLSERVER_USER_DB=Human_2025_Users
```

Cập nhật thông tin đăng nhập database phù hợp với môi trường của bạn.

### 6. Chạy ứng dụng

```bash
uvicorn main:app --reload
```

API sẽ khả dụng tại http://localhost:8000

## Tài liệu API

Sau khi ứng dụng chạy, bạn có thể truy cập:

- Tài liệu API (Swagger): http://localhost:8000/docs
- Tài liệu API thay thế (ReDoc): http://localhost:8000/redoc

## Cấu trúc dự án

```
HSSMP_backend/
├── main.py                # Entry point của ứng dụng
├── requirements.txt       # Các thư viện phụ thuộc
├── src/                   # Mã nguồn
│   ├── core/              # Module cốt lõi (cấu hình, v.v.)
│   ├── databases/         # Kết nối cơ sở dữ liệu
│   ├── models/            # Data models và schemas cho API
│   ├── routers/           # Định tuyến API
│   ├── schemas/           # Schema định nghĩa cấu trúc các bảng
│   ├── utils/             # Các hàm tiện ích xử lý logic
│   └── _utils.py          # Các hàm tiện ích chung
```

## Kết nối cơ sở dữ liệu

Dự án sử dụng SQLAlchemy để kết nối đồng thời với hai cơ sở dữ liệu:
- MySQL (payroll): quản lý lương và chấm công
- SQL Server (HUMAN_2025): quản lý thông tin nhân sự

Chuỗi kết nối được cấu hình trong các file trong thư mục `src/databases/` và được nạp từ biến môi trường.

## API Endpoints

### Quản lý nhân viên (`/employees`)

- `GET /employees`: Lấy danh sách nhân viên (phân trang)
- `GET /employees/search`: Tìm kiếm nhân viên theo nhiều tiêu chí
- `GET /employees/details/{employee_id}`: Xem chi tiết nhân viên
- `POST /employees/add`: Thêm nhân viên mới (đồng bộ hai hệ thống)
- `PUT /employees/update/{employee_id}`: Cập nhật thông tin nhân viên
- `DELETE /employees/delete/{employee_id}`: Xóa nhân viên
