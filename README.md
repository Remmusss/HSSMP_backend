# HSSMP Backend

Backend service for HSMP (ZENHRM SYSTEM MARAGEMENT PROJECT) integration project.

## Requirements

- Python 3.12+
- MySQL
- SQL Server (Microsoft)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Remmusss/HSSMP_backend.git
cd HSSMP_backend
```

### 2. Create a virtual environment

```bash
python -m venv env
```

### 3. Activate the virtual environment

On Windows:
```bash
env\Scripts\activate
```

On macOS/Linux:
```bash
source env/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

Tạo file `.env` ở src/core:
```
# App settings
APP_NAME=ZENHRM SYSTEM MARAGEMENT
APP_VERSION=0.1.0

# MySQL configuration
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=payroll

# SQL Server configuration
SQLSERVER_USER=your_sqlserver_username
SQLSERVER_PASSWORD=your_sqlserver_password
SQLSERVER_HOST=localhost
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=HUMAN_2025
```

Modify the database credentials as needed for your environment.

### 6. Run the application

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:

- API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## Project Structure

```
HSSMP_backend/
├── main.py                # Application entry point
├── requirements.txt       # Project dependencies
├── src/                   # Source code
│   ├── core/              # Core modules (config, etc.)
│   ├── models/            # Data models
│   └── utils/             # Utility functions
```

## Database Connection

This project uses SQLAlchemy to connect to both MySQL and SQL Server databases.
The connection strings are configured in `src/core/config.py` and are loaded from environment variables. 
