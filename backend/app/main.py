from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import excel

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Excel Manager API",
    description="Excel文件管理系统API",
    version="1.0.0"
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


@app.get("/")
def root():
    return {"message": "Excel Manager API", "docs": "/docs"}
