from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api import router as api_router
from app.database import connect_to_mongo, close_mongo_connection
from app.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="小说生成网站",
    description="智能小说生成和主角扮演体验平台",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    try:
        # 连接到MongoDB
        await connect_to_mongo()
        print("MongoDB连接成功")
    except Exception as e:
        print(f"MongoDB连接失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    try:
        # 关闭MongoDB连接
        await close_mongo_connection()
        print("MongoDB连接已关闭")
    except Exception as e:
        print(f"关闭MongoDB连接失败: {e}")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "小说生成网站API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
