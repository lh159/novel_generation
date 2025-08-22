from beanie import Document
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RequiredCharacter(BaseModel):
    """必须使用的汉字"""
    pinyin: str = Field(..., description="拼音")
    character: str = Field(..., description="汉字")


class WritingGuideline(BaseModel):
    """写作指导"""
    world_building: str = Field(..., description="世界观设定")
    character_development: str = Field(..., description="角色刻画")
    background_setting: str = Field(..., description="背景设定")
    plot_development: str = Field(..., description="情节发展")
    language_style: str = Field(..., description="语言风格")


class Material(Document):
    """小说构建材料"""
    
    title: str = Field(..., description="材料标题")
    category: str = Field(..., description="小说类别")
    example_novels: List[str] = Field(default=[], description="示例小说")
    writing_guidelines: WritingGuideline = Field(..., description="写作指导")
    required_characters: List[RequiredCharacter] = Field(default=[], description="构建小说必须用到的字")
    pinyin_character_count: int = Field(default=0, description="拼音汉字对数")
    
    # 元数据
    file_name: Optional[str] = Field(None, description="原始文件名")
    file_content: Optional[str] = Field(None, description="原始文件内容")
    upload_time: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True, description="是否激活")
    
    class Settings:
        name = "materials"
        
    class Config:
        json_schema_extra = {
            "example": {
                "title": "东方玄幻",
                "category": "第01类: 东方玄幻",
                "example_novels": ["苟在初圣魔门当人材", "夜无疆"],
                "writing_guidelines": {
                    "world_building": "构建独特的修炼体系，如境界划分",
                    "character_development": "主角通常从底层开始",
                    "background_setting": "设定丰富的修炼资源",
                    "plot_development": "以修炼升级为主线",
                    "language_style": "运用古典诗词意境"
                },
                "required_characters": [
                    {"pinyin": "shěng", "character": "省"},
                    {"pinyin": "nān", "character": "囡"}
                ],
                "pinyin_character_count": 26
            }
        }


class MaterialCreate(BaseModel):
    """创建材料请求"""
    title: str
    category: str
    example_novels: List[str] = []
    writing_guidelines: WritingGuideline
    required_characters: List[RequiredCharacter] = []
    pinyin_character_count: int = 0
    file_content: Optional[str] = None


class MaterialResponse(BaseModel):
    """材料响应"""
    id: str
    title: str
    category: str
    example_novels: List[str]
    writing_guidelines: WritingGuideline
    required_characters: List[RequiredCharacter]
    pinyin_character_count: int
    upload_time: datetime
    is_active: bool
