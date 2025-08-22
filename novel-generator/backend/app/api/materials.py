from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from ..models.material import Material, MaterialCreate, MaterialResponse
from ..services.material_parser import MaterialParser

router = APIRouter()
material_parser = MaterialParser()


@router.get("/", response_model=List[MaterialResponse])
async def get_materials(active_only: bool = True):
    """获取所有材料"""
    try:
        query = {"is_active": True} if active_only else {}
        materials = await Material.find(query).to_list()
        return [MaterialResponse(**material.dict()) for material in materials]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取材料列表失败: {str(e)}")


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: str):
    """获取单个材料"""
    try:
        material = await Material.get(material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        return MaterialResponse(**material.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取材料失败: {str(e)}")


@router.post("/upload")
async def upload_material_file(file: UploadFile = File(...)):
    """上传材料文件（支持md格式）"""
    try:
        # 检查文件格式
        if not file.filename.endswith(('.md', '.markdown', '.txt')):
            raise HTTPException(status_code=400, detail="仅支持 .md, .markdown, .txt 格式文件")
        
        # 读取文件内容
        content = await file.read()
        file_content = content.decode('utf-8')
        
        # 解析材料内容
        material_data = material_parser.parse_material_file(file_content, file.filename)
        
        # 创建材料记录
        material = Material(**material_data)
        await material.insert()
        
        # 返回适合前端的格式
        material_dict = material.dict()
        material_dict["id"] = str(material.id)  # 转换ObjectId为字符串
        
        return {
            "message": "文件上传成功",
            "categories": [
                {
                    "id": str(material.id),
                    "name": material.title,
                    "description": material.category
                }
            ],
            "categories_count": 1,
            "material": MaterialResponse(**material_dict)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/", response_model=MaterialResponse)
async def create_material(material_data: MaterialCreate):
    """手动创建材料"""
    try:
        material = Material(**material_data.dict())
        await material.insert()
        return MaterialResponse(**material.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建材料失败: {str(e)}")


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(material_id: str, material_data: MaterialCreate):
    """更新材料"""
    try:
        material = await Material.get(material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        # 更新字段
        for field, value in material_data.dict(exclude_unset=True).items():
            setattr(material, field, value)
        
        await material.save()
        return MaterialResponse(**material.dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新材料失败: {str(e)}")


@router.delete("/{material_id}")
async def delete_material(material_id: str, hard_delete: bool = False):
    """删除材料（软删除或硬删除）"""
    try:
        material = await Material.get(material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if hard_delete:
            await material.delete()
            return {"message": "材料已永久删除"}
        else:
            material.is_active = False
            await material.save()
            return {"message": "材料已停用"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除材料失败: {str(e)}")


@router.get("/{material_id}/validate")
async def validate_material(material_id: str):
    """验证材料完整性"""
    try:
        material = await Material.get(material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        validation_result = material_parser.validate_material(material)
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证材料失败: {str(e)}")


@router.get("/category/{category}")
async def get_materials_by_category(category: str):
    """按类别获取材料"""
    try:
        materials = await Material.find({"category": category, "is_active": True}).to_list()
        return [MaterialResponse(**material.dict()) for material in materials]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类材料失败: {str(e)}")