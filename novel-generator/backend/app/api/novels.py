from fastapi import APIRouter, HTTPException
from typing import List, Optional
from bson import ObjectId

from ..models.novel import Novel, NovelCreateRequest, NovelResponse, ChapterResponse
from ..services.novel_generator import NovelGenerator

router = APIRouter()


@router.post("/", response_model=NovelResponse)
async def create_novel(request: NovelCreateRequest):
    """创建新小说"""
    try:
        # 创建新小说文档
        novel = Novel(
            title=request.title,
            description=request.description,
            genre=request.genre,
            style=request.style,
            character_info=request.character_info,
            plot_outline=request.plot_outline,
            status="pending"
        )
        
        # 保存到数据库
        await novel.save()
        
        return novel.to_response()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建小说失败: {str(e)}")


@router.get("/", response_model=List[NovelResponse])
async def get_novels(skip: int = 0, limit: int = 20):
    """获取小说列表"""
    try:
        novels = await Novel.find_all().skip(skip).limit(limit).to_list()
        return [novel.to_response() for novel in novels]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取小说列表失败: {str(e)}")


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: str):
    """获取指定小说"""
    try:
        if not ObjectId.is_valid(novel_id):
            raise HTTPException(status_code=400, detail="无效的小说ID")
        
        novel = await Novel.get(ObjectId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        return novel.to_response()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取小说失败: {str(e)}")


@router.post("/{novel_id}/generate")
async def generate_novel_content(novel_id: str, material_id: Optional[str] = None):
    """生成小说内容（支持材料投喂）"""
    try:
        if not ObjectId.is_valid(novel_id):
            raise HTTPException(status_code=400, detail="无效的小说ID")
        
        novel = await Novel.get(ObjectId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        if novel.status == "generating":
            raise HTTPException(status_code=400, detail="小说正在生成中，请稍后重试")
        
        # 更新状态为生成中
        await novel.update_status("generating")
        
        try:
            # 使用AI生成内容
            generator = NovelGenerator()
            content = await generator.generate_novel_content(
                title=novel.title,
                description=novel.description,
                genre=novel.genre,
                style=novel.style,
                character_info=novel.character_info,
                plot_outline=novel.plot_outline,
                material_id=material_id
            )
            
            # 更新小说内容
            await novel.update_content(content)
            await novel.update_status("completed")
            
            return {"success": True, "message": "小说生成完成"}
            
        except Exception as e:
            # 生成失败，更新状态
            await novel.update_status("failed")
            raise HTTPException(status_code=500, detail=f"小说生成失败: {str(e)}")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


@router.post("/{novel_id}/generate-with-validation")
async def generate_novel_with_validation(novel_id: str, material_id: str, max_retries: int = 3):
    """使用材料验证生成小说（确保必须字符使用率达标）"""
    try:
        if not ObjectId.is_valid(novel_id):
            raise HTTPException(status_code=400, detail="无效的小说ID")
        
        novel = await Novel.get(ObjectId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        if novel.status == "generating":
            raise HTTPException(status_code=400, detail="小说正在生成中，请稍后重试")
        
        # 更新状态为生成中
        await novel.update_status("generating")
        
        try:
            # 使用小说生成器的验证模式
            generator = NovelGenerator()
            result = await generator.generate_with_material_validation(
                title=novel.title,
                description=novel.description,
                genre=novel.genre,
                style=novel.style,
                character_info=novel.character_info,
                plot_outline=novel.plot_outline,
                material_id=material_id,
                max_retries=max_retries
            )
            
            # 更新小说内容和状态
            await novel.update_content(result["content"])
            await novel.update_status("completed" if result["success"] else "failed")
            
            return {
                "success": result["success"],
                "message": f"小说生成完成（尝试{result['attempt']}次）",
                "character_usage_analysis": result["analysis"]
            }
            
        except Exception as e:
            # 生成失败，更新状态
            await novel.update_status("failed")
            raise HTTPException(status_code=500, detail=f"小说生成失败: {str(e)}")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


@router.post("/{novel_id}/chapters")
async def add_chapter(novel_id: str, chapter_number: int, title: str, content: str):
    """添加章节"""
    try:
        if not ObjectId.is_valid(novel_id):
            raise HTTPException(status_code=400, detail="无效的小说ID")
        
        novel = await Novel.get(ObjectId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        # 检查章节号是否已存在
        existing_chapter = next(
            (chapter for chapter in novel.chapters if chapter["chapter_number"] == chapter_number),
            None
        )
        if existing_chapter:
            raise HTTPException(status_code=400, detail="章节号已存在")
        
        # 添加章节
        await novel.add_chapter(chapter_number, title, content)
        
        return {"success": True, "message": "章节添加成功"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"添加章节失败: {str(e)}")


@router.get("/{novel_id}/chapters", response_model=List[ChapterResponse])
async def get_chapters(novel_id: str):
    """获取小说章节列表"""
    try:
        if not ObjectId.is_valid(novel_id):
            raise HTTPException(status_code=400, detail="无效的小说ID")
        
        novel = await Novel.get(ObjectId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        chapters = [
            ChapterResponse(
                chapter_number=chapter["chapter_number"],
                title=chapter["title"],
                content=chapter["content"],
                created_at=chapter["created_at"]
            )
            for chapter in sorted(novel.chapters, key=lambda x: x["chapter_number"])
        ]
        
        return chapters
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取章节列表失败: {str(e)}")


@router.get("/{novel_id}/chapters/{chapter_number}", response_model=ChapterResponse)
async def get_chapter(novel_id: str, chapter_number: int):
    """获取指定章节"""
    try:
        if not ObjectId.is_valid(novel_id):
            raise HTTPException(status_code=400, detail="无效的小说ID")
        
        novel = await Novel.get(ObjectId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        # 查找指定章节
        chapter = next(
            (chapter for chapter in novel.chapters if chapter["chapter_number"] == chapter_number),
            None
        )
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        return ChapterResponse(
            chapter_number=chapter["chapter_number"],
            title=chapter["title"],
            content=chapter["content"],
            created_at=chapter["created_at"]
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取章节失败: {str(e)}")


@router.delete("/{novel_id}")
async def delete_novel(novel_id: str):
    """删除小说"""
    try:
        if not ObjectId.is_valid(novel_id):
            raise HTTPException(status_code=400, detail="无效的小说ID")
        
        novel = await Novel.get(ObjectId(novel_id))
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        await novel.delete()
        
        return {"success": True, "message": "小说删除成功"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除小说失败: {str(e)}")