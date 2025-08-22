from fastapi import APIRouter, HTTPException
from typing import List, Optional
import uuid
from datetime import datetime
from ..models.dialogue import NovelSession, DialogueResponse, ProgressRequest, SessionCreate
from ..models.novel import Novel
from ..services.dialogue_parser import DialogueParser

router = APIRouter()
dialogue_parser = DialogueParser()


@router.post("/sessions", response_model=DialogueResponse)
async def create_session(request: SessionCreate):
    """创建新的阅读会话"""
    try:
        # 检查小说是否存在
        novel = await Novel.get(request.novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        if not novel.content:
            raise HTTPException(status_code=400, detail="小说内容为空，无法开始阅读")
        
        # 解析小说内容为对话片段
        dialogue_segments = dialogue_parser.parse_novel_content(novel.content)
        
        # 创建会话
        session_id = str(uuid.uuid4())
        session = NovelSession(
            novel_id=request.novel_id,
            user_id=request.user_id,
            session_id=session_id,
            dialogue_segments=dialogue_segments,
            total_segments=len(dialogue_segments),
            current_segment_index=0
        )
        
        # 设置初始状态
        if dialogue_segments:
            first_segment = dialogue_segments[0]
            if first_segment.speaker_type == "protagonist":
                session.is_waiting_for_protagonist = True
                session.current_protagonist_dialogue = first_segment.content
        
        await session.insert()
        
        return DialogueResponse(
            session_id=session_id,
            current_segment=dialogue_segments[0] if dialogue_segments else None,
            is_waiting_for_protagonist=session.is_waiting_for_protagonist,
            progress_percentage=0.0,
            total_segments=len(dialogue_segments),
            completed_segments=0,
            can_continue=len(dialogue_segments) > 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.get("/sessions/{session_id}", response_model=DialogueResponse)
async def get_session(session_id: str):
    """获取会话当前状态"""
    try:
        session = await NovelSession.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        current_segment = None
        if session.current_segment_index < len(session.dialogue_segments):
            current_segment = session.dialogue_segments[session.current_segment_index]
        
        return DialogueResponse(
            session_id=session_id,
            current_segment=current_segment,
            is_waiting_for_protagonist=session.is_waiting_for_protagonist,
            progress_percentage=session.progress_percentage,
            total_segments=session.total_segments,
            completed_segments=session.completed_segments,
            can_continue=session.current_segment_index < len(session.dialogue_segments)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话失败: {str(e)}")


@router.post("/sessions/{session_id}/progress", response_model=DialogueResponse)
async def progress_dialogue(session_id: str, request: ProgressRequest):
    """推进对话剧情"""
    try:
        session = await NovelSession.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 检查是否可以继续
        if session.current_segment_index >= len(session.dialogue_segments):
            raise HTTPException(status_code=400, detail="小说已阅读完毕")
        
        current_segment = session.dialogue_segments[session.current_segment_index]
        
        # 如果当前是主角对话且等待确认
        if session.is_waiting_for_protagonist and current_segment.speaker_type == "protagonist":
            if not request.confirm_read:
                raise HTTPException(status_code=400, detail="需要确认已读主角对话")
            
            # 标记当前主角对话为已读
            session.dialogue_segments[session.current_segment_index].is_read = True
            session.completed_segments += 1
            session.current_segment_index += 1
            session.is_waiting_for_protagonist = False
            session.current_protagonist_dialogue = None
        else:
            # 非主角对话，自动推进
            session.completed_segments += 1
            session.current_segment_index += 1
        
        # 更新进度
        session.progress_percentage = (session.completed_segments / session.total_segments) * 100
        
        # 检查下一个片段
        next_segment = None
        if session.current_segment_index < len(session.dialogue_segments):
            next_segment = session.dialogue_segments[session.current_segment_index]
            
            # 如果下一个是主角对话，设置等待状态
            if next_segment.speaker_type == "protagonist":
                session.is_waiting_for_protagonist = True
                session.current_protagonist_dialogue = next_segment.content
        
        session.updated_at = datetime.now()
        session.last_activity = datetime.now()
        await session.save()
        
        return DialogueResponse(
            session_id=session_id,
            current_segment=next_segment,
            is_waiting_for_protagonist=session.is_waiting_for_protagonist,
            progress_percentage=session.progress_percentage,
            total_segments=session.total_segments,
            completed_segments=session.completed_segments,
            can_continue=session.current_segment_index < len(session.dialogue_segments)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推进对话失败: {str(e)}")


@router.get("/sessions/{session_id}/history")
async def get_dialogue_history(session_id: str, limit: int = 50):
    """获取对话历史记录"""
    try:
        session = await NovelSession.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 返回已完成的对话片段
        completed_segments = [
            segment for segment in session.dialogue_segments[:session.current_segment_index]
            if segment.speaker_type == "protagonist" and segment.is_read
        ]
        
        # 限制返回数量
        if limit > 0:
            completed_segments = completed_segments[-limit:]
        
        return {
            "session_id": session_id,
            "history": completed_segments,
            "total_completed": len(completed_segments)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        session = await NovelSession.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        await session.delete()
        return {"message": "会话已删除"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")


@router.get("/sessions/{session_id}/stats")
async def get_session_stats(session_id: str):
    """获取会话统计信息"""
    try:
        session = await NovelSession.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 统计各类型对话数量
        protagonist_dialogues = len([s for s in session.dialogue_segments if s.speaker_type == "protagonist"])
        character_dialogues = len([s for s in session.dialogue_segments if s.speaker_type == "character"])
        narrator_segments = len([s for s in session.dialogue_segments if s.speaker_type == "narrator"])
        
        # 统计已读主角对话
        read_protagonist_dialogues = len([s for s in session.dialogue_segments 
                                        if s.speaker_type == "protagonist" and s.is_read])
        
        return {
            "session_id": session_id,
            "total_segments": session.total_segments,
            "completed_segments": session.completed_segments,
            "progress_percentage": session.progress_percentage,
            "protagonist_dialogues": protagonist_dialogues,
            "character_dialogues": character_dialogues,
            "narrator_segments": narrator_segments,
            "read_protagonist_dialogues": read_protagonist_dialogues,
            "created_at": session.created_at,
            "last_activity": session.last_activity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")