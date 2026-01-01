from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .database import engine, Base
from .routers import excel, auth
from .config import SESSION_SECRET

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Excel Manager API",
    description="Excel文件管理系统API",
    version="1.0.0"
)

# 添加 Session 中间件
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    max_age=None  # Session 过期时间由数据库控制
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(excel.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Excel Manager API", "docs": "/docs"}
