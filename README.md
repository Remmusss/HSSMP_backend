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

## API Endpoints và Phân quyền

Hệ thống có 4 vai trò người dùng:
- `Admin`: Có toàn quyền trên hệ thống
- `HR Manager`: Quản lý thông tin nhân viên và báo cáo nhân sự
- `Payroll Manager`: Quản lý lương và chấm công
- `Employee`: Người dùng thông thường

### Xác thực người dùng (`/`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/login` | POST | Đăng nhập và lấy token | Tất cả |
| `/refresh` | POST | Làm mới token | Đã đăng nhập |
| `/me` | GET | Xem thông tin người dùng hiện tại | Đã đăng nhập |

### Quản lý hồ sơ cá nhân (`/profile`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/profile` | GET | Xem thông tin cá nhân | Đã đăng nhập |

### Quản lý nhân viên (`/employees`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/employees` | GET | Danh sách nhân viên (phân trang) | Admin, HR Manager |
| `/employees/search` | GET | Tìm kiếm nhân viên | Admin, HR Manager |
| `/employees/details/{employee_id}` | GET | Chi tiết nhân viên | Admin, HR Manager |
| `/employees/add` | POST | Thêm nhân viên mới (đồng bộ) | Admin, HR Manager |
| `/employees/update/{employee_id}` | PUT | Cập nhật thông tin nhân viên | Admin, HR Manager |
| `/employees/delete/{employee_id}` | DELETE | Xóa nhân viên | Admin, HR Manager |

### Quản lý lương (`/payroll`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/payroll` | GET | Danh sách bảng lương (phân trang) | Admin, Payroll Manager |
| `/payroll/search` | GET | Tìm kiếm bảng lương | Admin, Payroll Manager |
| `/payroll/update/{payroll_id}` | PUT | Cập nhật thông tin lương | Admin, Payroll Manager |
| `/payroll/attendance` | GET | Danh sách chấm công (phân trang) | Admin, Payroll Manager |

### Quản lý phòng ban (`/departments`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/departments` | GET | Danh sách phòng ban | Admin, HR Manager, Payroll Manager |
| `/departments/add` | POST | Thêm phòng ban mới (đồng bộ) | Admin, HR Manager |
| `/departments/update/{department_id}` | PUT | Cập nhật thông tin phòng ban | Admin, HR Manager |
| `/departments/delete/{department_id}` | DELETE | Xóa phòng ban | Admin, HR Manager |

### Quản lý chức vụ (`/positions`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/positions` | GET | Danh sách chức vụ | Admin, HR Manager, Payroll Manager |
| `/positions/distribution/{position_id}` | GET | Phân bố nhân viên theo phòng ban | Admin, HR Manager, Payroll Manager |
| `/positions/add` | POST | Thêm chức vụ mới (đồng bộ) | Admin, HR Manager |
| `/positions/update/{position_id}` | PUT | Cập nhật thông tin chức vụ | Admin, HR Manager |
| `/positions/delete/{position_id}` | DELETE | Xóa chức vụ | Admin, HR Manager |

### Báo cáo thống kê (`/reports`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/reports/hr` | GET | Báo cáo nhân sự | Admin, HR Manager |
| `/reports/payroll` | GET | Báo cáo lương | Admin, Payroll Manager |
| `/reports/dividend` | GET | Báo cáo cổ tức | Admin |

### Thông báo (`/notifications`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/anniversaries` | GET | Lấy thông báo về ngày kỷ niệm của nhân viên sắp tới trong 30 ngày | Đã đăng nhập |
| `/absent-days-warning` | GET | Lấy thông báo về số ngày nghỉ phép của TẤT CẢ nhân viên trong 3 tháng gần đây | Admin, HR Manager, Payroll Manager |
| `/absent-days-personal-warning` | GET | Lấy thông báo về số ngày nghỉ phép của nhân viên trong 3 tháng gần đây | Đã đăng nhập |
| `/salary-gap-warning` | GET | Lấy thông báo về sự chênh lệch lương giữa 2 tháng gần đây của TẤT CẢ nhân viên | Admin, HR Manager, Payroll Manager |
| `/salary-gap-warning-personal` | GET | Lấy thông báo về sự chênh lệch lương giữa 2 tháng gần đây của bản thân | Đã đăng nhập |

### Quản lý tài khoản (`/admin`)

| Endpoint | Phương thức | Mô tả | Quyền truy cập |
|----------|-------------|-------|----------------|
| `/admin/create_user` | POST | Tạo tài khoản cho nhân viên | Admin |
| `/admin/update_user/{username}` | PUT | Cập nhật tài khoản cho nhân viên | Admin |
