from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os
from datetime import datetime

from ..services.outline_generator import OutlineGenerator
from ..services.deepseek_outline_generator import DeepSeekOutlineGenerator
from ..services.chapter_generator import ChapterGenerator
from ..services.material_parser import MaterialParser
from ..models.material import Material
from ..models.chapter_novel import ChapterNovel, ChapterInfo, NovelStatus, ChapterStatus
from ..config import settings

router = APIRouter()

# 请求/响应模型
class NovelCreateRequest(BaseModel):
    title: str
    chapter_count: int = 10
    material_ids: List[str] = []

class OutlineResponse(BaseModel):
    title: str
    summary: str
    main_characters: List[Dict[str, str]]
    chapters: List[Dict[str, Any]]

class ChapterGenerateRequest(BaseModel):
    target_length: int = 2000

class NovelResponse(BaseModel):
    id: str
    title: str
    outline: Optional[Dict[str, Any]]
    total_chapters: int
    completed_chapters: int
    status: str
    created_at: str

class ChapterResponse(BaseModel):
    id: str
    chapter_number: int
    title: str
    content: Optional[str]
    summary: Optional[str]
    word_count: int
    status: str

# 全局变量存储生成器实例
outline_generator = None
chapter_generator = None
material_parser = None

def get_outline_generator():
    global outline_generator
    if outline_generator is None:
        # 使用配置文件中的API密钥
        openai_key = os.getenv("OPENAI_API_KEY")
        deepseek_key = settings.deepseek_api_key
        
        if openai_key:
            outline_generator = OutlineGenerator(openai_key)
        elif deepseek_key:
            outline_generator = DeepSeekOutlineGenerator(deepseek_key)
        else:
            raise ValueError("需要配置OPENAI_API_KEY或DEEPSEEK_API_KEY")
    return outline_generator

def get_chapter_generator():
    global chapter_generator
    if chapter_generator is None:
        # 使用配置文件中的API密钥
        api_key = os.getenv("OPENAI_API_KEY") or settings.deepseek_api_key
        if not api_key:
            raise ValueError("需要配置OPENAI_API_KEY或DEEPSEEK_API_KEY")
        chapter_generator = ChapterGenerator(api_key)
    return chapter_generator

def get_material_parser():
    global material_parser
    if material_parser is None:
        material_parser = MaterialParser()
    return material_parser

@router.post("/", response_model=NovelResponse)
async def create_novel(request: NovelCreateRequest):
    """创建新小说（只创建基本信息，不生成内容）"""
    try:
        # 创建新小说记录
        novel = ChapterNovel(
            title=request.title,
            total_chapters=request.chapter_count,
            material_ids=request.material_ids,
            status=NovelStatus.PLANNING
        )
        
        await novel.save()
        
        return NovelResponse(
            id=str(novel.id),
            title=novel.title,
            outline=novel.outline,
            total_chapters=novel.total_chapters,
            completed_chapters=novel.completed_chapters,
            status=novel.status.value,
            created_at=novel.created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建小说失败: {str(e)}")

class OutlineGenerateRequest(BaseModel):
    material_ids: List[str] = []
    required_words: List[str] = []

@router.post("/{novel_id}/outline")
async def generate_outline(
    novel_id: str, 
    request: OutlineGenerateRequest,
    outline_gen: OutlineGenerator = Depends(get_outline_generator)
):
    """生成小说大纲"""
    try:
        # 获取小说
        novel = await ChapterNovel.get(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        if novel.status == NovelStatus.WRITING:
            raise HTTPException(status_code=400, detail="小说已开始写作，无法重新生成大纲")
        
        # 获取材料
        materials = []
        if request.material_ids:
            from bson import ObjectId
            # 转换字符串ID为ObjectId
            object_ids = []
            for mid in request.material_ids:
                try:
                    object_ids.append(ObjectId(mid))
                except:
                    print(f"警告: 无效的材料ID {mid}")
            
            if object_ids:
                material_docs = await Material.find({"_id": {"$in": object_ids}}).to_list()
                materials = [material.to_dict() for material in material_docs]
        
        # 生成大纲
        if isinstance(outline_gen, DeepSeekOutlineGenerator):
            outline_data = await outline_gen.generate_outline(
                title=novel.title,
                materials=materials,
                chapter_count=novel.total_chapters,
                required_words=request.required_words
            )
        else:
            outline_data = outline_gen.generate_outline(
                title=novel.title,
                materials=materials,
                chapter_count=novel.total_chapters
            )
        
        # 保存大纲
        novel.outline = outline_data
        novel.status = NovelStatus.OUTLINED
        novel.updated_at = datetime.now()
        await novel.save()
        
        # 创建章节记录
        for chapter_info in outline_data["chapters"]:
            chapter = ChapterInfo(
                novel_id=str(novel.id),
                chapter_number=chapter_info["number"],
                title=chapter_info["title"],
                summary=chapter_info["summary"],
                status=ChapterStatus.PLANNED
            )
            await chapter.save()
        
        return {
            "success": True,
            "message": "大纲生成完成",
            "outline": outline_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成大纲失败: {str(e)}")

@router.get("/{novel_id}/outline", response_model=OutlineResponse)
async def get_outline(novel_id: str):
    """获取小说大纲"""
    try:
        novel = await ChapterNovel.get(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        if not novel.outline:
            raise HTTPException(status_code=404, detail="大纲尚未生成")
        
        return OutlineResponse(**novel.outline)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取大纲失败: {str(e)}")

@router.post("/{novel_id}/chapters/{chapter_number}/generate")
async def generate_chapter(
    novel_id: str,
    chapter_number: int,
    request: ChapterGenerateRequest = ChapterGenerateRequest(),
    material_ids: List[str] = [],
    chapter_gen: ChapterGenerator = Depends(get_chapter_generator)
):
    """生成指定章节"""
    try:
        # 获取小说和章节
        novel = await ChapterNovel.get(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        chapter = await ChapterInfo.find_one(
            ChapterInfo.novel_id == novel_id,
            ChapterInfo.chapter_number == chapter_number
        )
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        if chapter.status == ChapterStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="章节已生成完成")
        
        # 获取大纲信息
        if not novel.outline:
            raise HTTPException(status_code=400, detail="请先生成小说大纲")
        
        chapter_info = next(
            (ch for ch in novel.outline["chapters"] if ch["number"] == chapter_number),
            None
        )
        if not chapter_info:
            raise HTTPException(status_code=404, detail="大纲中未找到该章节信息")
        
        # 获取前面已完成的章节内容
        previous_chapters = await ChapterInfo.find(
            ChapterInfo.novel_id == novel_id,
            ChapterInfo.chapter_number < chapter_number,
            ChapterInfo.status == ChapterStatus.COMPLETED
        ).sort(ChapterInfo.chapter_number).to_list()
        
        previous_contents = [ch.content for ch in previous_chapters if ch.content]
        
        # 获取材料
        materials = []
        if material_ids:
            from bson import ObjectId
            # 转换字符串ID为ObjectId
            object_ids = []
            for mid in material_ids:
                try:
                    object_ids.append(ObjectId(mid))
                except:
                    print(f"警告: 无效的材料ID {mid}")
            
            if object_ids:
                material_docs = await Material.find({"_id": {"$in": object_ids}}).to_list()
                materials = [material.to_dict() for material in material_docs]
        
        # 更新章节状态
        chapter.status = ChapterStatus.WRITING
        chapter.updated_at = datetime.now()
        await chapter.save()
        
        # 生成章节内容
        result = chapter_gen.generate_chapter(
            novel_title=novel.title,
            chapter_info=chapter_info,
            previous_chapters=previous_contents,
            materials=materials,
            target_length=request.target_length
        )
        
        # 保存章节内容
        chapter.content = result["content"]
        chapter.word_count = result["word_count"]
        chapter.status = ChapterStatus.COMPLETED if result["status"] == "completed" else ChapterStatus.FAILED
        chapter.updated_at = datetime.now()
        await chapter.save()
        
        # 更新小说状态
        if chapter.status == ChapterStatus.COMPLETED:
            await novel.update_completed_count()
        
        return {
            "success": True,
            "message": f"第{chapter_number}章生成完成",
            "chapter": {
                "number": chapter.chapter_number,
                "title": chapter.title,
                "content": chapter.content,
                "word_count": chapter.word_count,
                "status": chapter.status.value
            }
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"生成章节失败: {str(e)}")

@router.get("/", response_model=List[NovelResponse])
async def get_novels(skip: int = 0, limit: int = 20):
    """获取小说列表"""
    try:
        novels = await ChapterNovel.find().skip(skip).limit(limit).to_list()
        return [
            NovelResponse(
                id=str(novel.id),
                title=novel.title,
                outline=novel.outline,
                total_chapters=novel.total_chapters,
                completed_chapters=novel.completed_chapters,
                status=novel.status.value,
                created_at=novel.created_at.isoformat()
            )
            for novel in novels
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取小说列表失败: {str(e)}")

@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: str):
    """获取指定小说"""
    try:
        novel = await ChapterNovel.get(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        return NovelResponse(
            id=str(novel.id),
            title=novel.title,
            outline=novel.outline,
            total_chapters=novel.total_chapters,
            completed_chapters=novel.completed_chapters,
            status=novel.status.value,
            created_at=novel.created_at.isoformat()
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取小说失败: {str(e)}")

@router.get("/{novel_id}/chapters", response_model=List[ChapterResponse])
async def get_chapters(novel_id: str):
    """获取小说章节列表"""
    try:
        chapters = await ChapterInfo.find(ChapterInfo.novel_id == novel_id).sort(ChapterInfo.chapter_number).to_list()
        return [
            ChapterResponse(
                id=str(chapter.id),
                chapter_number=chapter.chapter_number,
                title=chapter.title,
                content=chapter.content,
                summary=chapter.summary,
                word_count=chapter.word_count,
                status=chapter.status.value
            )
            for chapter in chapters
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取章节列表失败: {str(e)}")

@router.get("/{novel_id}/chapters/{chapter_number}", response_model=ChapterResponse)
async def get_chapter(novel_id: str, chapter_number: int):
    """获取指定章节"""
    try:
        chapter = await ChapterInfo.find_one(
            ChapterInfo.novel_id == novel_id,
            ChapterInfo.chapter_number == chapter_number
        )
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        return ChapterResponse(
            id=str(chapter.id),
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            content=chapter.content,
            summary=chapter.summary,
            word_count=chapter.word_count,
            status=chapter.status.value
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取章节失败: {str(e)}")

@router.delete("/{novel_id}")
async def delete_novel(novel_id: str):
    """删除小说"""
    try:
        novel = await ChapterNovel.get(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        # 删除相关章节
        await ChapterInfo.find(ChapterInfo.novel_id == novel_id).delete()
        
        # 删除小说
        await novel.delete()
        
        return {"success": True, "message": "小说删除成功"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除小说失败: {str(e)}")
