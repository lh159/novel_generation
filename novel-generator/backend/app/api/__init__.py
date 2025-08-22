from fastapi import APIRouter
from .materials import router as materials_router
from .novels import router as novels_router
from .novels_new import router as novels_new_router
from .dialogue import router as dialogue_router
from ..routes.chapter_dialogue import router as chapter_dialogue_router

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(materials_router, prefix="/materials", tags=["材料管理"])
router.include_router(novels_router, prefix="/novels", tags=["小说管理"])
router.include_router(novels_new_router, prefix="/novels-v2", tags=["章节小说系统"])
router.include_router(dialogue_router, prefix="/dialogue", tags=["对白交互"])
router.include_router(chapter_dialogue_router, prefix="/chapter-dialogue", tags=["章节对话交互"])
