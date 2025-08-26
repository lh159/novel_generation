#!/bin/bash

# 小说生成器启动脚本
# 用途：一键启动前端和后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}🚀 小说生成器启动脚本${NC}"
echo "=================================================="

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}📋 检查系统依赖...${NC}"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装${NC}"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装${NC}"
        exit 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未安装${NC}"
        exit 1
    fi
    
    # 检查MongoDB
    if ! command -v mongod &> /dev/null; then
        echo -e "${YELLOW}⚠️  MongoDB未安装，请先安装MongoDB${NC}"
        echo -e "${YELLOW}   macOS: brew install mongodb-community${NC}"
        echo -e "${YELLOW}   Ubuntu: sudo apt-get install mongodb${NC}"
        echo -e "${YELLOW}   或使用Docker: docker run -d -p 27017:27017 mongo${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 系统依赖检查通过${NC}"
}

# 清理端口
cleanup_ports() {
    echo -e "${YELLOW}🧹 清理端口占用...${NC}"
    
    # 清理特定服务的PID文件和进程
    for service in mongodb backend frontend; do
        if [ "$service" = "mongodb" ]; then
            pidfile="mongodb.pid"
        else
            pidfile="$service/$service.pid"
        fi
        
        if [ -f "$pidfile" ]; then
            PID=$(cat "$pidfile" 2>/dev/null || echo "")
            if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}  停止 $service 进程 (PID: $PID)${NC}"
                kill -TERM "$PID" 2>/dev/null || true
                sleep 2
                kill -KILL "$PID" 2>/dev/null || true
            fi
            rm -f "$pidfile"
        fi
    done
    
    # 强制终止占用端口的进程
    for port in 3000 8000 27017; do
        PIDS=$(lsof -ti :$port 2>/dev/null || echo "")
        if [ -n "$PIDS" ]; then
            echo -e "${YELLOW}  清理端口 $port 上的进程${NC}"
            echo "$PIDS" | xargs kill -9 2>/dev/null || true
        fi
    done
    
    # 等待端口释放
    sleep 3
    
    echo -e "${GREEN}✅ 端口清理完成${NC}"
}

# 启动MongoDB
start_mongodb() {
    echo -e "${YELLOW}🗄️  启动MongoDB数据库...${NC}"
    
    # 检查MongoDB是否已经运行
    if pgrep -x "mongod" > /dev/null; then
        echo -e "${GREEN}✅ MongoDB已经在运行${NC}"
        return
    fi
    
    # 创建数据目录
    MONGO_DATA_DIR="$PROJECT_ROOT/data/db"
    mkdir -p "$MONGO_DATA_DIR"
    
    # 启动MongoDB
    echo -e "${YELLOW}🚀 启动MongoDB服务器...${NC}"
    nohup mongod --dbpath "$MONGO_DATA_DIR" --port 27017 --bind_ip 127.0.0.1 > mongodb.log 2>&1 &
    MONGO_PID=$!
    echo $MONGO_PID > mongodb.pid
    
    # 等待MongoDB启动
    echo -e "${YELLOW}⏳ 等待MongoDB启动...${NC}"
    for i in {1..30}; do
        # 尝试使用新版mongosh或旧版mongo命令
        if mongosh --eval "db.adminCommand('ismaster')" > /dev/null 2>&1 || mongo --eval "db.adminCommand('ismaster')" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ MongoDB启动成功 (PID: $MONGO_PID)${NC}"
            echo -e "${GREEN}   地址: mongodb://localhost:27017${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ MongoDB启动超时${NC}"
            exit 1
        fi
        sleep 1
    done
}

# 启动后端
start_backend() {
    echo -e "${YELLOW}🔧 启动后端服务...${NC}"
    
    cd "$BACKEND_DIR"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 创建Python虚拟环境...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查并安装依赖
    echo -e "${YELLOW}📦 检查Python依赖...${NC}"
    
    # 使用更可靠的依赖检查方式
    REQUIREMENTS_HASH=$(md5sum requirements.txt 2>/dev/null | cut -d' ' -f1 || echo "")
    INSTALLED_HASH=""
    if [ -f ".deps_hash" ]; then
        INSTALLED_HASH=$(cat .deps_hash 2>/dev/null || echo "")
    fi
    
    # 只有当requirements.txt变化时才重新安装
    if [ "$REQUIREMENTS_HASH" != "$INSTALLED_HASH" ] || [ ! -d "venv/lib" ]; then
        echo -e "${YELLOW}📦 安装/更新Python依赖...${NC}"
        pip install -r requirements.txt
        echo "$REQUIREMENTS_HASH" > .deps_hash
    else
        echo -e "${GREEN}✅ Python依赖已是最新${NC}"
    fi
    
    # 后台启动FastAPI服务
    echo -e "${YELLOW}🚀 启动FastAPI服务器...${NC}"
    
    # 检查是否是开发环境，决定是否使用--reload
    if [ "${NOVEL_ENV:-development}" = "production" ]; then
        # 生产环境：不使用reload，更稳定
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    else
        # 开发环境：使用reload但限制监听范围，减少误触发
        nohup python3 -m uvicorn main:app --reload --reload-dir app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    fi
    
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    # 等待后端启动
    echo -e "${YELLOW}⏳ 等待后端启动...${NC}"
    
    # 增强的启动检查
    WAIT_TIME=60  # 增加等待时间到60秒
    for i in $(seq 1 $WAIT_TIME); do
        # 检查进程是否还在运行
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${RED}❌ 后端进程异常退出${NC}"
            echo -e "${YELLOW}📋 查看日志: tail -20 backend.log${NC}"
            exit 1
        fi
        
        # 检查健康状态
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
            echo -e "${GREEN}   地址: http://localhost:8000${NC}"
            break
        fi
        
        # 显示启动进度
        if [ $((i % 10)) -eq 0 ]; then
            echo -e "${YELLOW}   等待中... (${i}/${WAIT_TIME}秒)${NC}"
        fi
        
        if [ $i -eq $WAIT_TIME ]; then
            echo -e "${RED}❌ 后端启动超时${NC}"
            echo -e "${YELLOW}📋 后端日志:${NC}"
            tail -10 backend.log 2>/dev/null || echo "无法读取日志文件"
            exit 1
        fi
        sleep 1
    done
}

# 启动前端
start_frontend() {
    echo -e "${YELLOW}🌐 启动前端服务...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 安装npm依赖...${NC}"
        npm install
    fi
    
    # 后台启动Vite开发服务器
    echo -e "${YELLOW}🚀 启动Vite开发服务器...${NC}"
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    # 等待前端启动
    echo -e "${YELLOW}⏳ 等待前端启动...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
            echo -e "${GREEN}   地址: http://localhost:3000${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ 前端启动超时${NC}"
            exit 1
        fi
        sleep 1
    done
}

# 显示状态
show_status() {
    echo ""
    echo "=================================================="
    echo -e "${GREEN}🎉 小说生成器启动完成！${NC}"
    echo ""
    echo -e "${BLUE}📊 服务状态：${NC}"
    echo -e "  🗄️  MongoDB:   mongodb://localhost:27017"
    echo -e "  🔧 后端API:  http://localhost:8000"
    echo -e "  🌐 前端界面: http://localhost:3000"
    echo ""
    echo -e "${BLUE}📝 管理命令：${NC}"
    echo -e "  停止服务:   ./stop.sh"
    echo -e "  查看日志:   ./logs.sh"
    echo -e "  重启服务:   ./restart.sh"
    echo ""
    echo -e "${YELLOW}💡 提示: 使用 Ctrl+C 或运行 ./stop.sh 来停止服务${NC}"
    echo "=================================================="
}

# 主函数
main() {
    check_dependencies
    cleanup_ports
    start_mongodb
    start_backend
    start_frontend
    show_status
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}🛑 正在停止服务...${NC}"; ./stop.sh; exit 0' INT TERM

# 运行主函数
main "$@"
