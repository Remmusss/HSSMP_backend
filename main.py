from fastapi import FastAPI
from fastapi.responses import JSONResponse


# Phần import các router
from src.core.config import app_conf
# from src.auth.routers import router as auth_router

app = FastAPI(
    title=app_conf.APP_NAME,
    version=app_conf.APP_VERSION
)


# Đăng ký các router vào ứng dụng FastAPI
# app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/")
async def hello():
    return JSONResponse({app.title: app.version})