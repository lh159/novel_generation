import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.novel import Novel
from app.models.material import Material
from app.models.dialogue import NovelSession


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    """连接到MongoDB"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "novel_generator")
    
    # 创建MongoDB客户端
    mongodb.client = AsyncIOMotorClient(mongodb_url)
    mongodb.database = mongodb.client[database_name]
    
    # 初始化Beanie ODM
    from .models.chapter_novel import ChapterNovel, ChapterInfo
    
    await init_beanie(
        database=mongodb.database,
        document_models=[Novel, Material, NovelSession, ChapterNovel, ChapterInfo]
    )
    
    print(f"Connected to MongoDB: {mongodb_url}/{database_name}")


async def close_mongo_connection():
    """关闭MongoDB连接"""
    if mongodb.client:
        mongodb.client.close()
        print("MongoDB connection closed")


def get_database():
    """获取数据库实例"""
    return mongodb.database