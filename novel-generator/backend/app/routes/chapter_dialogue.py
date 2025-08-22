from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import connect_to_mongo
from app.models.chapter_novel import ChapterNovel, ChapterInfo
# from app.services.deepseek_client import DeepSeekClient  # 已移除DeepSeek依赖
from app.services.protagonist_roleplay import ProtagonistRoleplaySystem
import os
import json
import re
import uuid
from datetime import datetime

router = APIRouter()

class DialogueRequest(BaseModel):
    novel_id: str
    chapter_number: int
    session_id: Optional[str] = None

class ConfirmDialogueRequest(BaseModel):
    session_id: str

# 存储会话状态
sessions = {}

# 主角扮演系统实例
roleplay_system = ProtagonistRoleplaySystem()

async def extract_dialogues_from_chapter(chapter_content):
    """从章节内容中提取对话 - 支持新的标记格式（正文：、主角：、角色名：）"""
    import time
    start_time = time.time()
    print(f"🔍 开始解析章节内容，长度: {len(chapter_content)} 字符")
    
    try:
        # 快速检查是否有标记格式
        if '正文：' in chapter_content or '主角：' in chapter_content:
            print("检测到标记格式，使用快速标记解析...")
            marked_dialogues = await _parse_marked_content(chapter_content)
            if marked_dialogues:
                elapsed = time.time() - start_time
                print(f"✅ 标记解析完成，耗时: {elapsed:.2f}秒，提取 {len(marked_dialogues)} 个对话")
                return marked_dialogues
            
        # 如果没有找到标记格式，使用简单的本地分析方法
        print("未找到标记格式，使用快速分段方法...")
        result = await _fallback_extract_dialogues(chapter_content)
        elapsed = time.time() - start_time
        print(f"✅ 回退解析完成，耗时: {elapsed:.2f}秒，提取 {len(result)} 个对话")
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 对话提取错误，耗时: {elapsed:.2f}秒，错误: {e}")
        # 最终回退到简单分段方法
        return await _fallback_extract_dialogues(chapter_content)

async def _parse_marked_content(chapter_content):
    """解析带有标记的章节内容（正文：、主角：、角色名：）"""
    dialogues = []
    lines = chapter_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 处理正文：标记（旁白内容）
        if line.startswith('正文：'):
            text = line[3:].strip()  # 去掉"正文："标记
            if text:
                dialogues.append({
                    "speaker": "旁白",
                    "text": text,
                    "type": "narration",
                    "is_protagonist": False,
                    "required_chars_used": []
                })
                
        # 处理主角：标记（主角对话）
        elif line.startswith('主角：'):
            text = line[3:].strip()  # 去掉"主角："标记
            if text:
                dialogues.append({
                    "speaker": "主角",
                    "text": text,
                    "type": "dialogue",
                    "is_protagonist": True,
                    "required_chars_used": []
                })
                
        # 处理其他角色对话（格式：角色名：对话内容）
        elif '：' in line:
            colon_index = line.find('：')
            speaker = line[:colon_index].strip()
            text = line[colon_index + 1:].strip()
            
            # 验证这是一个有效的角色对话
            # 1. 说话者名字不能为空且不能太长（避免误判标题）
            # 2. 对话内容不能为空
            # 3. 不是章节标题（不以"第"开头）
            if (speaker and text and 
                len(speaker) <= 20 and  # 角色名不会太长
                not speaker.startswith('第') and  # 不是章节标题
                not speaker in ['正文', '主角']):  # 不是已处理的标记
                
                dialogues.append({
                    "speaker": speaker,
                    "text": text,
                    "type": "dialogue",
                    "is_protagonist": False,  # 非主角对话
                    "required_chars_used": []
                })
    
    print(f"标记解析完成，共提取 {len(dialogues)} 个段落")
    print(f"其中：旁白 {len([d for d in dialogues if d['type'] == 'narration'])} 个，对话 {len([d for d in dialogues if d['type'] == 'dialogue'])} 个")
    return dialogues

# DeepSeek相关代码已移除 - 使用本地解析方法

# 辅助函数已移除 - 使用标记格式直接解析

async def _fallback_extract_dialogues(chapter_content):
    """回退方法：简单分段处理"""
    try:
        dialogues = []
        lines = chapter_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 简单快速判断是否包含对话
            has_dialogue = any(quote in line for quote in ['"', '"', '"', '「', '」'])
            
            if has_dialogue:
                dialogues.append({
                    "speaker": "未知",
                    "text": line,
                    "type": "dialogue",
                    "is_protagonist": False,
                    "required_chars_used": []
                })
            else:
                dialogues.append({
                    "speaker": "旁白",
                    "text": line,
                    "type": "narration",
                    "is_protagonist": False,
                    "required_chars_used": []
                })
        
        return dialogues
        
    except Exception as e:
        print(f"回退分段处理错误: {e}")
        return []

@router.get("/debug/{novel_id}")
async def debug_novel_content(novel_id: str):
    """调试接口：检查小说和章节内容"""
    try:
        # 获取小说信息
        novel = await ChapterNovel.get(novel_id)
        if not novel:
            return {"error": "小说不存在", "novel_id": novel_id}
            
        # 获取所有章节
        chapters = await novel.get_chapters()
        
        result = {
            "novel": {
                "id": str(novel.id),
                "title": novel.title,
                "description": novel.description,
                "total_chapters": novel.total_chapters,
                "completed_chapters": novel.completed_chapters,
                "status": novel.status.value
            },
            "chapters": []
        }
        
        for chapter in chapters:
            chapter_info = {
                "id": str(chapter.id),
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "status": chapter.status.value,
                "word_count": chapter.word_count,
                "has_content": bool(chapter.content),
                "content_length": len(chapter.content) if chapter.content else 0,
                "content_preview": chapter.content[:200] + "..." if chapter.content and len(chapter.content) > 200 else chapter.content
            }
            result["chapters"].append(chapter_info)
            
        return result
        
    except Exception as e:
        print(f"调试接口错误: {e}")
        return {"error": str(e), "novel_id": novel_id}

@router.get("/chapter/{novel_id}/{chapter_number}")
async def get_chapter_dialogues(novel_id: str, chapter_number: int):
    """获取章节中的所有对话"""
    try:
        # 获取小说和章节信息
        novel = await ChapterNovel.get(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
            
        # 获取指定章节
        chapter = await novel.get_chapter(chapter_number)
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        # 检查章节内容
        if not chapter.content:
            raise HTTPException(status_code=404, detail="章节内容为空")
        
        # 从章节内容中提取对话
        dialogues = await extract_dialogues_from_chapter(chapter.content)
        
        return {
            "novel_id": novel_id,
            "chapter_number": chapter_number,
            "chapter_title": chapter.title,
            "chapter_status": chapter.status.value,
            "content_length": len(chapter.content),
            "dialogues": dialogues,
            "total_dialogues": len([d for d in dialogues if d["type"] == "dialogue"])
        }
        
    except Exception as e:
        print(f"获取章节对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/current")
async def get_current_chapter_dialogue(request: DialogueRequest):
    """获取当前章节对话"""
    try:
        # 处理会话
        session_id = request.session_id
        dialogues = None
        
        if session_id and session_id in sessions:
            # 已有会话，直接使用缓存的对话数据
            print(f"📋 使用已有会话: {session_id}")
            session = sessions[session_id]
            dialogues = session["dialogues"]
        else:
            # 新会话，需要解析章节内容
            print(f"🆕 创建新会话，解析章节内容...")
            
            # 获取小说和章节信息
            novel = await ChapterNovel.get(request.novel_id)
            if not novel:
                raise HTTPException(status_code=404, detail="小说不存在")
                
            # 获取指定章节
            chapter = await novel.get_chapter(request.chapter_number)
            if not chapter:
                raise HTTPException(status_code=404, detail="章节不存在")
            
            # 从章节内容中提取对话（只在新会话时执行）
            dialogues = await extract_dialogues_from_chapter(chapter.content)
            
            if not dialogues:
                raise HTTPException(status_code=404, detail="章节中没有找到对话内容")
            
            # 创建新会话
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "novel_id": request.novel_id,
                "chapter_number": request.chapter_number,
                "dialogues": dialogues,
                "dialogue_history": [],
                "created_at": datetime.now()
            }
            # 创建角色扮演会话
            roleplay_system.active_sessions[session_id] = {
                'novel_id': request.novel_id,
                'current_chapter': request.chapter_number,
                'dialogue_history': [],
                'current_dialogue_index': 0,
                'waiting_for_user_confirmation': False,
                'current_protagonist_dialogue': None
            }
            print(f"✅ 新会话创建完成: {session_id}, 对话数量: {len(dialogues)}")
        
        # 获取当前对话状态
        current_dialogue = roleplay_system.get_current_dialogue(session_id, dialogues)
        current_dialogue["session_id"] = session_id
        
        return current_dialogue
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取当前章节对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/advance")
async def advance_chapter_dialogue(request: ConfirmDialogueRequest):
    """推进章节对话（用于非主角对话的自动推进）"""
    import time
    start_time = time.time()
    print(f"🚀 [/advance] 开始处理请求，session_id: {request.session_id}")
    
    try:
        if request.session_id not in sessions:
            print(f"❌ [/advance] 会话不存在: {request.session_id}")
            raise HTTPException(status_code=400, detail="无效的会话ID")
        
        session = sessions[request.session_id]
        dialogues = session["dialogues"]
        
        print(f"📋 [/advance] 会话存在，对话数量: {len(dialogues) if dialogues else 0}")
        
        if not dialogues:
            print(f"❌ [/advance] dialogues 为空！这很异常")
            raise HTTPException(status_code=500, detail="对话数据为空")
        
        # 推进对话并获取下一个对话
        print(f"🔄 [/advance] 调用 roleplay_system.advance_dialogue...")
        next_dialogue = roleplay_system.advance_dialogue(request.session_id, dialogues)
        
        elapsed = time.time() - start_time
        print(f"✅ [/advance] 处理完成，耗时: {elapsed:.3f}秒")
        
        next_dialogue["session_id"] = request.session_id
        return next_dialogue
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"推进章节对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm")
async def confirm_chapter_dialogue(request: ConfirmDialogueRequest):
    """确认章节对话"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=400, detail="无效的会话ID")
        
        session = sessions[request.session_id]
        dialogues = session["dialogues"]
        
        # 确认主角对话并获取下一个对话
        next_dialogue = roleplay_system.confirm_protagonist_dialogue(request.session_id, dialogues)
        
        if "error" in next_dialogue:
            raise HTTPException(status_code=400, detail=next_dialogue["error"])
        
        next_dialogue["session_id"] = request.session_id
        return next_dialogue
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"确认章节对话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chapter_dialogue_history(session_id: str):
    """获取章节对话历史"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=400, detail="无效的会话ID")
        
        session = sessions[session_id]
        return {
            "session_id": session_id,
            "dialogue_history": session["dialogue_history"],
            "created_at": session["created_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取章节对话历史错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
