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
# from src.routers.human import human_router
# from src.routers.payroll import payroll_router
from src.routers.employees import employees_router as employee_router


# uvicorn main:app --host 192.168.102.12 --reload
app = FastAPI(
    title="ZENHRM SYSTEM MANAGEMENT",
    description="App quản lý nhân sự và bảng lương",
    version="1.0.0"
)


# app.include_router(auth_router, prefix="/auth")
# app.include_router(human_router, prefix="/human")
# app.include_router(payroll_router, prefix="/payroll")
app.include_router(employee_router, prefix="/employees")

@app.get("/")
async def hello():
    return RedirectResponse(url="/docs")