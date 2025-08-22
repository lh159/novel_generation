# 小说生成网站

一个智能小说生成和主角扮演体验平台，用户可以通过投喂小说材料，系统自动生成对应的小说内容，并提供沉浸式的主角扮演体验。

## 🚀 核心功能

- **材料投喂系统**: 支持上传《构建小说所需材料.md》文件
- **小说生成引擎**: 基于AI自动生成包含大量对白的小说
- **沉浸式主角扮演**: 用户扮演主角，通过阅读和确认推进剧情
- **智能剧情控制**: 主角对白暂停等待，其他角色对白自动推进

## 🏗️ 技术架构

### 后端
- **Python 3.9+** + **FastAPI**
- **PostgreSQL** + **SQLAlchemy ORM**
- **Redis** 缓存
- **OpenAI API** 小说生成

### 前端
- **React 18** + **TypeScript**
- **Ant Design** UI组件库
- **Vite** 构建工具
- **Zustand** 状态管理

## 📦 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd novel-generator
```

### 2. 使用Docker Compose启动（推荐）
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 手动启动

#### 后端
```bash
cd backend
pip install -r requirements.txt

# 设置环境变量
cp env.example .env
# 编辑.env文件，填入你的配置

# 启动后端服务
python main.py
```

#### 前端
```bash
cd frontend
npm install

# 启动开发服务器
npm run dev
```

## 🌐 访问地址

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: localhost:5432
- **Redis**: localhost:6379

## 📚 使用说明

### 1. 上传材料
1. 访问网站首页
2. 上传《构建小说所需材料.md》文件
3. 系统自动解析小说类别和必需汉字

### 2. 生成小说
1. 选择感兴趣的小说类别
2. 点击"开始创作"
3. 系统使用AI生成完整小说内容

### 3. 体验主角扮演
1. 选择生成的小说
2. 开始主角扮演体验
3. 阅读主角台词，点击"确认读完"继续剧情
4. 其他角色对白自动推进

## 🔧 开发说明

### 项目结构
```
novel-generator/
├── backend/                 # 后端代码
│   ├── app/                # 应用代码
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据库模型
│   │   ├── services/      # 业务逻辑
│   │   └── config.py      # 配置文件
│   ├── main.py            # 主应用文件
│   └── requirements.txt   # Python依赖
├── frontend/               # 前端代码
│   ├── src/               # 源代码
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # Vite配置
├── database/               # 数据库相关
├── docs/                   # 文档
└── docker-compose.yml      # Docker配置
```

### 数据库设计
- **novel_categories**: 小说类别表
- **novels**: 小说表
- **dialogues**: 对白表
- **user_sessions**: 用户会话表

## 🚀 部署

### 生产环境
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d
```

### 环境变量
- `DATABASE_URL`: PostgreSQL连接字符串
- `REDIS_URL`: Redis连接字符串
- `OPENAI_API_KEY`: OpenAI API密钥
- `SECRET_KEY`: 应用密钥

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
