# 小说生成器管理脚本使用说明

这里提供了一套完整的脚本来管理前后端服务，让你可以轻松启动、停止和监控你的小说生成网站。

## 📋 系统要求

### 必需软件
- **Python 3.8+**: 后端API服务
- **Node.js 16+**: 前端开发环境
- **MongoDB 4.4+**: 数据库服务

### MongoDB安装

**macOS (使用Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

**Ubuntu/Debian:**
```bash
# 导入MongoDB公钥
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -

# 添加MongoDB源
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

# 安装MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# 启动MongoDB服务
sudo systemctl start mongod
sudo systemctl enable mongod
```

**使用Docker（推荐用于开发）:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## 🚀 快速开始

### 启动服务
```bash
./start.sh
```
这个命令会：
- ✅ 检查系统依赖（Python3, Node.js, npm, MongoDB）
- 🧹 清理端口占用（3000, 8000, 27017）
- 🗄️ 启动MongoDB数据库
- 🔧 启动后端服务（FastAPI）
- 🌐 启动前端服务（Vite）
- 📊 显示服务状态和访问地址

### 停止服务
```bash
./stop.sh
```
这个命令会：
- 🛑 优雅停止前后端服务和MongoDB
- 🧹 清理进程和端口占用
- 📊 显示最终状态

### 重启服务
```bash
./restart.sh
```
等同于先运行 `./stop.sh` 再运行 `./start.sh`

### 查看日志
```bash
./logs.sh                    # 查看所有日志
./logs.sh mongodb            # 只查看MongoDB日志
./logs.sh backend            # 只查看后端日志
./logs.sh frontend           # 只查看前端日志
./logs.sh -f backend         # 实时跟踪后端日志
./logs.sh -n 100 mongodb     # 显示MongoDB最后100行日志
```

## 📊 服务信息

### MongoDB数据库
- **端口**: 27017
- **地址**: mongodb://localhost:27017
- **数据目录**: `data/db/`
- **日志文件**: `mongodb.log`
- **PID文件**: `mongodb.pid`

### 后端服务 (FastAPI)
- **端口**: 8000
- **地址**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **日志文件**: `backend/backend.log`
- **PID文件**: `backend/backend.pid`

### 前端服务 (Vite)
- **端口**: 3000
- **地址**: http://localhost:3000
- **开发服务器**: 支持热重载
- **日志文件**: `frontend/frontend.log`
- **PID文件**: `frontend/frontend.pid`

## 🔧 故障排除

### 常见问题

**1. 端口被占用**
```bash
# 检查端口占用
lsof -i :27017,8000,3000

# 强制清理端口
./stop.sh
```

**2. 服务启动失败**
```bash
# 查看详细日志
./logs.sh mongodb
./logs.sh backend
./logs.sh frontend

# 重启服务
./restart.sh
```

**3. 依赖问题**
```bash
# 检查MongoDB安装
mongod --version

# 重新安装后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重新安装前端依赖
cd frontend
npm install
```

**4. 权限问题**
```bash
# 给脚本添加执行权限
chmod +x *.sh
```

### 日志位置
- MongoDB日志: `mongodb.log`
- 后端日志: `backend/backend.log`
- 前端日志: `frontend/frontend.log`
- 启动脚本会自动创建这些日志文件

### 进程管理
脚本使用PID文件来跟踪服务进程：
- `mongodb.pid` - MongoDB进程ID
- `backend/backend.pid` - 后端进程ID
- `frontend/frontend.pid` - 前端进程ID

如果进程意外退出，这些文件会被自动清理。

### MongoDB数据目录
- 数据存储: `data/db/`
- 自动创建数据目录
- 数据持久化保存

## 🎯 开发工作流

### 日常开发
```bash
# 1. 启动开发环境
./start.sh

# 2. 开发代码（支持热重载）
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# 数据库: mongodb://localhost:27017

# 3. 查看日志（如需要）
./logs.sh -f all

# 4. 停止服务
./stop.sh
```

### 生产部署前测试
```bash
# 清理并重启
./stop.sh --clean-logs
./start.sh

# 验证服务状态
mongosh --eval "db.adminCommand('ismaster')"  # 检查MongoDB
curl http://localhost:8000/health             # 检查后端API
curl http://localhost:3000                    # 检查前端
```

## 🔒 安全注意事项

1. **生产环境**：修改CORS设置，限制允许的域名
2. **数据库安全**：配置MongoDB认证和访问控制
3. **环境变量**：检查 `backend/.env` 配置
4. **端口访问**：确保防火墙设置正确
5. **日志安全**：定期清理敏感信息
6. **数据备份**：定期备份MongoDB数据

## 🎉 享受开发

现在你可以专注于小说生成功能的开发，而不用担心服务管理的问题！

---

**提示**: 所有脚本都有详细的输出信息和错误处理，如果遇到问题，请查看终端输出和日志文件。
