from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NovelStatus(str, Enum):
    PLANNING = "planning"
    OUTLINED = "outlined"
    WRITING = "writing"
    COMPLETED = "completed"
    PAUSED = "paused"

class ChapterStatus(str, Enum):
    PLANNED = "planned"
    WRITING = "writing"
    COMPLETED = "completed"
    FAILED = "failed"

class ChapterInfo(Document):
    """章节信息文档"""
    novel_id: str = Field(..., description="所属小说ID")
    chapter_number: int = Field(..., description="章节序号")
    title: str = Field(..., description="章节标题")
    summary: Optional[str] = Field(None, description="章节摘要")
    content: Optional[str] = Field(None, description="章节内容")
    word_count: int = Field(default=0, description="字数统计")
    status: ChapterStatus = Field(default=ChapterStatus.PLANNED, description="章节状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Settings:
        name = "chapters"
        indexes = [
            [("novel_id", 1), ("chapter_number", 1)],  # 复合索引
            "novel_id",
            "status"
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "novel_id": self.novel_id,
            "chapter_number": self.chapter_number,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "word_count": self.word_count,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ChapterNovel(Document):
    """章节式小说文档"""
    title: str = Field(..., description="小说标题")
    description: Optional[str] = Field(None, description="小说描述")
    outline: Optional[Dict[str, Any]] = Field(None, description="小说大纲")
    total_chapters: int = Field(default=10, description="总章节数")
    completed_chapters: int = Field(default=0, description="已完成章节数")
    status: NovelStatus = Field(default=NovelStatus.PLANNING, description="小说状态")
    material_ids: List[str] = Field(default_factory=list, description="关联的材料ID列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Settings:
        name = "chapter_novels"
        indexes = [
            "title",
            "status",
            "created_at"
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "outline": self.outline,
            "total_chapters": self.total_chapters,
            "completed_chapters": self.completed_chapters,
            "status": self.status.value,
            "material_ids": self.material_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    async def get_chapters(self) -> List[ChapterInfo]:
        """获取所有章节"""
        return await ChapterInfo.find(ChapterInfo.novel_id == str(self.id)).sort(ChapterInfo.chapter_number).to_list()
    
    async def get_chapter(self, chapter_number: int) -> Optional[ChapterInfo]:
        """获取指定章节"""
        return await ChapterInfo.find_one(
            ChapterInfo.novel_id == str(self.id),
            ChapterInfo.chapter_number == chapter_number
        )
    
    async def update_completed_count(self):
        """更新已完成章节数"""
        completed_count = await ChapterInfo.find(
            ChapterInfo.novel_id == str(self.id),
            ChapterInfo.status == ChapterStatus.COMPLETED
        ).count()
        
        self.completed_chapters = completed_count
        
        # 更新小说状态
        if completed_count >= self.total_chapters:
            self.status = NovelStatus.COMPLETED
        elif completed_count > 0:
            self.status = NovelStatus.WRITING
        
        self.updated_at = datetime.now()
        await self.save()
