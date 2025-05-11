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

# from src.routers.auth import auth_router
from src.routers.employees import employees_router
from src.routers.payroll import payroll_router


# uvicorn main:app --reload
app = FastAPI(
    title="ZENHRM SYSTEM MANAGEMENT",
    description="App quản lý nhân sự và bảng lương",
    version="1.0.0"
)


# app.include_router(auth_router, prefix="/auth")
app.include_router(employees_router, prefix="/employees")
app.include_router(payroll_router, prefix="/payroll")

@app.get("/")
async def hello():
    return RedirectResponse(url="/docs")