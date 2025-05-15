USE HUMAN_2025;
GO

DELETE FROM Dividends;
DELETE FROM Employees;
DELETE FROM Positions;
DELETE FROM Departments;

DBCC CHECKIDENT ('Departments', RESEED, 0);
DBCC CHECKIDENT ('Positions', RESEED, 0);
DBCC CHECKIDENT ('Employees', RESEED, 0);
DBCC CHECKIDENT ('Dividends', RESEED, 0);

-- Chèn lại Departments
INSERT INTO Departments (DepartmentName) VALUES
(N'Nhân sự'),
(N'Kế toán'),
(N'Công nghệ thông tin'),
(N'Marketing'),
(N'Kinh doanh');

-- Chèn lại Positions
INSERT INTO Positions (PositionName) VALUES
(N'Nhân viên'),
(N'Quản lý'),
(N'Chuyên viên'),
(N'Giám đốc'),
(N'Trợ lý');

-- Chèn lại Employees
INSERT INTO Employees (FullName, DateOfBirth, Gender, PhoneNumber, Email, HireDate, DepartmentID, PositionID, Status) VALUES
(N'Nguyễn Văn An', '1990-05-15', N'Nam', '0905123456', 'an.nguyen@email.com', '2020-01-10', 1, 1, N'Active'),
(N'Trần Thị Bình', '1992-08-22', N'Nữ', '0916234567', 'binh.tran@email.com', '2019-03-15', 2, 3, N'Active'),
(N'Lê Minh Châu', '1988-11-30', N'Nam', '0927345678', 'chau.le@email.com', '2021-06-20', 3, 2, N'Inactive'),
(N'Phạm Thị Duyên', '1995-02-14', N'Nữ', '0938456789', 'duyen.pham@email.com', '2022-09-01', 4, 1, N'Active'),
(N'Hoàng Văn Em', '1993-07-07', N'Nam', '0949567890', 'ex.hoang@email.com', '2018-12-05', 5, 4, N'Inactive'),
(N'Vũ Thị Ngô', '1991-04-25', N'Nữ', '0950678901', 'fleur.vu@email.com', '2020-11-11', 1, 3, N'Active'),
(N'Đỗ Quang Giang', '1989-09-18', N'Nam', '0961789012', 'giang.do@email.com', '2017-07-22', 2, 2, N'Active'),
(N'Bùi Thị Hà', '1994-12-03', N'Nữ', '0972890123', 'ha.bui@email.com', '2023-02-28', 3, 5, N'Inactive'),
(N'Ngô Văn Linh', '1990-06-10', N'Nam', '0983901234', 'inh.ngo@email.com', '2019-10-15', 4, 1, N'Inactive'),
(N'Mai Thị Khánh', '1996-03-27', N'Nữ', '0994012345', 'khanh.mai@email.com', '2021-08-30', 5, 3, N'Active');

-- Chèn lại Dividends
INSERT INTO Dividends (EmployeeID, DividendAmount, DividendDate) VALUES
(1, 5000000.00, '2024-01-15'),
(1, 3000000.00, '2024-07-20'),
(2, 4500000.00, '2024-03-10'),
(2, 6000000.00, '2024-09-05'),
(2, 2000000.00, '2025-01-12'),
(3, 7000000.00, '2024-02-25'),
(3, 3500000.00, '2024-08-15'),
(4, 4000000.00, '2024-04-30'),
(4, 5500000.00, '2024-10-10'),
(4, 2500000.00, '2025-02-20'),
(5, 8000000.00, '2024-05-15'),
(5, 3000000.00, '2024-11-22'),
(6, 6500000.00, '2024-06-18'),
(6, 4000000.00, '2025-01-30'),
(6, 2000000.00, '2025-03-10'),
(7, 5000000.00, '2024-07-25'),
(7, 3500000.00, '2024-12-05'),
(8, 6000000.00, '2024-08-30'),
(8, 4500000.00, '2025-02-15'),
(8, 3000000.00, '2025-04-20'),
(9, 5500000.00, '2024-09-12'),
(9, 4000000.00, '2025-03-25'),
(10, 7000000.00, '2024-10-20'),
(10, 5000000.00, '2025-01-05'),
(10, 2500000.00, '2025-04-10'),
(1, 6000000.00, '2025-03-15'),
(3, 4500000.00, '2025-04-05'),
(5, 3000000.00, '2025-02-28'),
(7, 4000000.00, '2025-03-30'),
(9, 3500000.00, '2025-04-15');