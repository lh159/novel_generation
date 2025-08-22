from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import BaseModel, Field
from bson import ObjectId


class NovelCreateRequest(BaseModel):
    title: str = Field(..., description="小说标题")
    description: str = Field(..., description="小说描述")
    genre: str = Field(..., description="小说类型")
    style: str = Field(..., description="写作风格")
    character_info: str = Field(..., description="人物信息")
    plot_outline: str = Field(..., description="情节大纲")


class NovelResponse(BaseModel):
    id: str = Field(..., description="小说ID")
    title: str = Field(..., description="小说标题")
    description: str = Field(..., description="小说描述")
    genre: str = Field(..., description="小说类型")
    style: str = Field(..., description="写作风格")
    character_info: str = Field(..., description="人物信息")
    plot_outline: str = Field(..., description="情节大纲")
    content: Optional[str] = Field(None, description="小说内容")
    status: str = Field(..., description="生成状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ChapterResponse(BaseModel):
    chapter_number: int = Field(..., description="章节号")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    created_at: datetime = Field(..., description="创建时间")


class Novel(Document):
    title: str = Field(..., description="小说标题")
    description: str = Field(..., description="小说描述")
    genre: str = Field(..., description="小说类型")
    style: str = Field(..., description="写作风格")
    character_info: str = Field(..., description="人物信息")
    plot_outline: str = Field(..., description="情节大纲")
    content: Optional[str] = Field(None, description="小说内容")
    status: str = Field(default="pending", description="生成状态: pending, generating, completed, failed")
    chapters: List[dict] = Field(default_factory=list, description="章节列表")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    class Settings:
        name = "novels"
        indexes = [
            "title",
            "genre",
            "status",
            "created_at",
        ]

    def to_response(self) -> NovelResponse:
        """转换为响应模型"""
        return NovelResponse(
            id=str(self.id),
            title=self.title,
            description=self.description,
            genre=self.genre,
            style=self.style,
            character_info=self.character_info,
            plot_outline=self.plot_outline,
            content=self.content,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    async def add_chapter(self, chapter_number: int, title: str, content: str):
        """添加章节"""
        chapter = {
            "chapter_number": chapter_number,
            "title": title,
            "content": content,
            "created_at": datetime.utcnow()
        }
        self.chapters.append(chapter)
        self.updated_at = datetime.utcnow()
        await self.save()

    async def update_status(self, status: str):
        """更新状态"""
        self.status = status
        self.updated_at = datetime.utcnow()
        await self.save()

    async def update_content(self, content: str):
        """更新内容"""
        self.content = content
        self.updated_at = datetime.utcnow()
        await self.save()