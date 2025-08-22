from beanie import Document
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SpeakerType(str, Enum):
    """对话者类型"""
    PROTAGONIST = "protagonist"  # 主角
    CHARACTER = "character"      # 其他角色
    NARRATOR = "narrator"        # 旁白/叙述


class DialogueSegment(BaseModel):
    """对话片段"""
    speaker_type: SpeakerType = Field(..., description="对话者类型")
    speaker_name: Optional[str] = Field(None, description="说话者姓名")
    content: str = Field(..., description="对话内容")
    sequence: int = Field(..., description="对话顺序")
    is_read: bool = Field(default=False, description="是否已读（主角对话专用）")
    required_chars_used: List[str] = Field(default=[], description="使用的必须汉字")


class NovelSession(Document):
    """小说阅读会话"""
    
    novel_id: str = Field(..., description="小说ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: str = Field(..., description="会话ID")
    
    # 对话系统
    dialogue_segments: List[DialogueSegment] = Field(default=[], description="对话片段列表")
    current_segment_index: int = Field(default=0, description="当前片段索引")
    
    # 进度跟踪
    total_segments: int = Field(default=0, description="总片段数")
    completed_segments: int = Field(default=0, description="已完成片段数")
    progress_percentage: float = Field(default=0.0, description="进度百分比")
    
    # 主角扮演状态
    is_waiting_for_protagonist: bool = Field(default=False, description="是否等待主角确认")
    current_protagonist_dialogue: Optional[str] = Field(None, description="当前主角对话")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "novel_sessions"


class DialogueResponse(BaseModel):
    """对话响应"""
    session_id: str
    current_segment: Optional[DialogueSegment]
    is_waiting_for_protagonist: bool
    progress_percentage: float
    total_segments: int
    completed_segments: int
    can_continue: bool


class ProgressRequest(BaseModel):
    """推进剧情请求"""
    confirm_read: bool = True


class SessionCreate(BaseModel):
    """创建会话请求"""
    novel_id: str
    user_id: Optional[str] = None
