import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "novel_generator"
    redis_url: str = "redis://localhost:6379"
    
    # DeepSeek API配置
    deepseek_api_key: Optional[str] = None
    deepseek_api_base: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-reasoner"
    
    # 应用配置
    secret_key: str = "your_secret_key_here"
    debug: bool = True
    allowed_hosts: str = "localhost,127.0.0.1"
    
    # 文件上传配置
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    class Config:
        env_file = ["env.local", ".env"]
        case_sensitive = False

settings = Settings()
