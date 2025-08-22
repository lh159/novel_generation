# 章节式小说生成系统

## 概述

这是一个基于MongoDB的章节式小说生成系统，支持分章节创作、大纲生成和内容管理。系统提供了完整的RESTful API接口，可以独立使用或集成到其他应用中。

## 功能特性

### 🎯 核心功能
- **小说创建**: 创建新的章节式小说项目
- **大纲生成**: 基于AI自动生成小说大纲和章节规划
- **章节管理**: 分章节生成内容，支持独立编辑
- **进度追踪**: 实时追踪写作进度和状态
- **材料整合**: 支持关联参考材料

### 📊 状态管理
- **小说状态**: planning → outlined → writing → completed
- **章节状态**: planned → writing → completed/failed

## API 接口

### 基础路径
```
http://localhost:8000/api/novels-v2
```

### 1. 小说管理

#### 创建小说
```http
POST /
Content-Type: application/json

{
    "title": "小说标题",
    "chapter_count": 10,
    "material_ids": ["material_id1", "material_id2"]
}
```

#### 获取小说列表
```http
GET /?skip=0&limit=20
```

#### 获取小说详情
```http
GET /{novel_id}
```

#### 删除小说
```http
DELETE /{novel_id}
```

### 2. 大纲管理

#### 生成大纲
```http
POST /{novel_id}/outline
Content-Type: application/json

["material_id1", "material_id2"]
```

#### 获取大纲
```http
GET /{novel_id}/outline
```

### 3. 章节管理

#### 生成章节
```http
POST /{novel_id}/chapters/{chapter_number}/generate
Content-Type: application/json

{
    "target_length": 2000
}
```

#### 获取章节列表
```http
GET /{novel_id}/chapters
```

#### 获取单个章节
```http
GET /{novel_id}/chapters/{chapter_number}
```

## 数据模型

### ChapterNovel (章节小说)
```python
{
    "id": "ObjectId",
    "title": "小说标题",
    "description": "小说描述",
    "outline": {
        "title": "标题",
        "summary": "简介",
        "main_characters": [...],
        "chapters": [...]
    },
    "total_chapters": 10,
    "completed_chapters": 3,
    "status": "writing",
    "material_ids": ["id1", "id2"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

### ChapterInfo (章节信息)
```python
{
    "id": "ObjectId",
    "novel_id": "小说ID",
    "chapter_number": 1,
    "title": "章节标题",
    "summary": "章节摘要",
    "content": "章节内容",
    "word_count": 2000,
    "status": "completed",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

## 使用流程

### 1. 创建小说项目
```python
import httpx

async def create_novel():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/novels-v2/",
            json={
                "title": "我的第一部小说",
                "chapter_count": 5,
                "material_ids": []
            }
        )
        novel = response.json()
        return novel["id"]
```

### 2. 生成大纲
```python
async def generate_outline(novel_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8000/api/novels-v2/{novel_id}/outline",
            json=[]  # 材料ID列表
        )
        return response.json()
```

### 3. 逐章生成内容
```python
async def generate_chapter(novel_id, chapter_number):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8000/api/novels-v2/{novel_id}/chapters/{chapter_number}/generate",
            json={"target_length": 2000}
        )
        return response.json()
```

## 前端演示

系统提供了一个完整的HTML演示页面 `chapter_novel_demo.html`，包含：

- 📝 小说创建界面
- 🎯 大纲生成和展示
- 📚 章节管理和生成
- 📊 进度跟踪
- 📋 小说列表管理

### 启动演示
1. 启动后端服务器
2. 在浏览器中打开 `chapter_novel_demo.html`
3. 按照界面提示操作

## 测试

### 自动化测试
运行测试脚本：
```bash
python test_chapter_api.py
```

测试覆盖：
- ✅ 小说创建
- ✅ 大纲生成
- ✅ 章节生成
- ✅ 数据查询
- ✅ 状态管理

## 配置要求

### 环境变量
```bash
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=novel_generator
OPENAI_API_KEY=your-openai-api-key
```

### 依赖包
```bash
pip install fastapi beanie motor pymongo openai
```

## 部署说明

### 1. 数据库初始化
系统会自动创建所需的MongoDB集合和索引。

### 2. 服务启动
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. 健康检查
```bash
curl http://localhost:8000/health
```

## 扩展功能

### 1. 材料管理
- 支持上传参考材料
- 材料可关联到小说和章节
- 自动解析材料内容

### 2. 批量操作
- 批量生成多个章节
- 批量导出小说内容
- 批量状态管理

### 3. 版本控制
- 章节内容版本管理
- 修改历史记录
- 回滚功能

## 故障排除

### 常见问题

1. **MongoDB连接失败**
   - 检查MongoDB服务是否启动
   - 验证连接字符串格式
   - 确认网络连接

2. **AI生成失败**
   - 检查OpenAI API密钥
   - 验证网络连接
   - 查看API配额限制

3. **章节生成卡住**
   - 检查前置章节状态
   - 验证大纲是否存在
   - 查看服务器日志

### 日志查看
```bash
tail -f logs/novel_generator.log
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件

---

📧 如有问题，请提交 Issue 或联系开发团队。
