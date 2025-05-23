USE payroll;

-- Tắt kiểm tra khóa ngoại để tránh lỗi ràng buộc khi truncate
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE attendance;
TRUNCATE TABLE salaries;
TRUNCATE TABLE employees;
TRUNCATE TABLE positions;
TRUNCATE TABLE departments;

-- Bật lại kiểm tra khóa ngoại
SET FOREIGN_KEY_CHECKS = 1;

-- Chèn dữ liệu vào bảng departments (đồng bộ từ SQL Server)
INSERT INTO departments (DepartmentID, DepartmentName) VALUES
(1, 'Nhân sự'),
(2, 'Kế toán'),
(3, 'Công nghệ thông tin'),
(4, 'Marketing'),
(5, 'Kinh doanh');

-- Chèn dữ liệu vào bảng positions (đồng bộ từ SQL Server)
INSERT INTO positions (PositionID, PositionName) VALUES
(1, 'Nhân viên'),
(2, 'Quản lý'),
(3, 'Chuyên viên'),
(4, 'Giám đốc'),
(5, 'Trợ lý');

-- Chèn dữ liệu vào bảng employees (đồng bộ từ SQL Server, lược bỏ các cột không có trong MySQL như DateOfBirth, Gender, PhoneNumber, Email, HireDate)
INSERT INTO employees (EmployeeID, FullName, DepartmentID, PositionID, Status) VALUES
(1, 'Nguyễn Văn An', 1, 1, 'Active'),
(2, 'Trần Thị Bình', 2, 3, 'Active'),
(3, 'Lê Minh Châu', 3, 2, 'Inactive'),
(4, 'Phạm Thị Duyên', 4, 1, 'Active'),
(5, 'Hoàng Văn Em', 5, 4, 'Inactive'),
(6, 'Vũ Thị Ngô', 1, 3, 'Activate'),
(7, 'Đỗ Quang Giang', 2, 2, 'Activate'),
(8, 'Bùi Thị Hà', 3, 5, 'Inactive'),
(9, 'Ngô Văn Linh', 4, 1, 'Inactive'),
(10, 'Mai Thị Khánh', 5, 3, 'Activate');

-- Chèn dữ liệu vào bảng attendance (dữ liệu mới, mỗi nhân viên có 1-2 bản ghi chấm công)
INSERT INTO attendance (EmployeeID, WorkDays, AbsentDays, LeaveDays, AttendanceMonth, CreatedAt) VALUES
(1, 20, 1, 1, '2024-01-01', NOW()),
(1, 21, 0, 1, '2024-07-01', NOW()),
(2, 19, 2, 1, '2024-03-01', NOW()),
(2, 20, 1, 1, '2024-09-01', NOW()),
(3, 22, 0, 0, '2024-02-01', NOW()),
(3, 20, 1, 1, '2024-08-01', NOW()),
(4, 21, 1, 0, '2024-04-01', NOW()),
(4, 19, 2, 1, '2024-10-01', NOW()),
(5, 20, 1, 1, '2024-05-01', NOW()),
(5, 21, 0, 1, '2024-11-01', NOW()),
(6, 22, 0, 0, '2024-06-01', NOW()),
(6, 20, 1, 1, '2025-01-01', NOW()),
(7, 21, 1, 0, '2024-07-01', NOW()),
(8, 20, 1, 1, '2024-08-01', NOW()),
(8, 19, 2, 1, '2025-02-01', NOW()),
(9, 21, 0, 1, '2024-09-01', NOW()),
(9, 20, 1, 1, '2025-03-01', NOW()),
(10, 22, 0, 0, '2024-10-01', NOW()),
(10, 21, 1, 0, '2025-04-01', NOW());

-- Chèn dữ liệu vào bảng salaries (dữ liệu mới, mỗi nhân viên có 1-2 bản ghi lương, đồng bộ với AttendanceMonth)
INSERT INTO salaries (EmployeeID, SalaryMonth, BaseSalary, Bonus, Deductions, NetSalary, CreatedAt) VALUES
-- EmployeeID 1: Chênh lệch dương > 30% (13,500,000 → 18,000,000)
(1, '2024-06-01', 12000000.00, 2000000.00, 500000.00, 13500000.00, NOW()),
(1, '2024-07-02', 12000000.00, 6300000.00, 300000.00, 18000000.00, NOW()),
-- EmployeeID 2: Chênh lệch âm > 30% (17,300,000 → 11,000,000)
(2, '2024-08-02', 15000000.00, 3000000.00, 700000.00, 17300000.00, NOW()),
(2, '2024-09-01', 15000000.00, 0.00, 4000000.00, 11000000.00, NOW()),
-- EmployeeID 3: Chênh lệch dương > 30% (21,200,000 → 28,000,000)
(3, '2024-07-01', 18000000.00, 4000000.00, 800000.00, 21200000.00, NOW()),
(3, '2024-08-02', 18000000.00, 10600000.00, 600000.00, 28000000.00, NOW()),
-- EmployeeID 4: Chênh lệch âm > 30% (10,600,000 → 7,000,000)
(4, '2024-09-01', 10000000.00, 1000000.00, 400000.00, 10600000.00, NOW()),
(4, '2024-10-02', 10000000.00, 0.00, 3000000.00, 7000000.00, NOW()),
-- EmployeeID 5: Chênh lệch dương > 30% (24,000,000 → 32,000,000)
(5, '2024-10-06', 20000000.00, 5000000.00, 1000000.00, 24000000.00, NOW()),
(5, '2024-11-08', 20000000.00, 12800000.00, 800000.00, 32000000.00, NOW()),
-- EmployeeID 6: Chênh lệch nhỏ < 30% (15,500,000 → 16,100,000, ~3.87%)
(6, '2024-12-12', 14000000.00, 2000000.00, 500000.00, 15500000.00, NOW()),
(6, '2025-01-01', 14000000.00, 2500000.00, 400000.00, 16100000.00, NOW()),
-- EmployeeID 7: Chỉ có 1 bản ghi, không cần chênh lệch
(7, '2024-07-01', 16000000.00, 3000000.00, 600000.00, 18400000.00, NOW()),
-- EmployeeID 8: Chênh lệch nhỏ < 30% (14,500,000 → 14,100,000, ~-2.76%)
(8, '2025-04-01', 13000000.00, 2000000.00, 500000.00, 14500000.00, NOW()),
(8, '2025-05-01', 13000000.00, 1500000.00, 400000.00, 14100000.00, NOW()),
-- EmployeeID 9: Chênh lệch nhỏ < 30% (11,700,000 → 12,100,000, ~3.42%)
(9, '2025-04-02', 11000000.00, 1000000.00, 300000.00, 11700000.00, NOW()),
(9, '2025-05-03', 11000000.00, 1500000.00, 400000.00, 12100000.00, NOW()),
-- EmployeeID 10: Chênh lệch nhỏ < 30% (20,300,000 → 19,900,000, ~-1.97%)
(10, '2025-04-01', 17000000.00, 4000000.00, 700000.00, 20300000.00, NOW()),
(10, '2025-05-01', 17000000.00, 3500000.00, 600000.00, 19900000.00, NOW());