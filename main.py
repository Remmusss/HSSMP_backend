from fastapi import FastAPI
from fastapi.responses import JSONResponse


# Phần import các router
# from src.auth.routers import router as auth_router
from src.core.config import app_conf

app = FastAPI(
    title=app_conf.app_name,
    version=app_conf.app_version
)


# Đăng ký các router vào ứng dụng FastAPI
# app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/")
async def hello():
    return JSONResponse({"status": "live"})