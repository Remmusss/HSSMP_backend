from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Request,
    Response,
    BackgroundTasks,
)
from fastapi.responses import RedirectResponse

from fastapi.middleware.cors import CORSMiddleware


from src.routers.auth import auth_router
from src.routers.profile import profile_router
from src.routers.employees import employees_router
from src.routers.payroll import payroll_router
from src.routers.departments import departments_router
from src.routers.positions import positions_router
from src.routers.reports import reports_router
from src.routers.notifications import notifications_router
from src.routers.admin import admin_router
from src.routers.dashboard import dashboard_router

# uvicorn main:app --reload

app = FastAPI(
    title="ZENHRM SYSTEM MANAGEMENT",
    description="App quản lý nhân sự và bảng lương",
    version="1.0.0",
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="")
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(profile_router, prefix="/profile")
app.include_router(employees_router, prefix="/employees")
app.include_router(payroll_router, prefix="/payroll")
app.include_router(departments_router, prefix="/departments")
app.include_router(positions_router, prefix="/positions")
app.include_router(reports_router, prefix="/reports")
app.include_router(notifications_router, prefix="/notifications")
app.include_router(admin_router, prefix="/admin")

@app.get("/")
async def hello():
    return RedirectResponse(url="/docs")
