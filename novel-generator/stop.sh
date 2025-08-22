#!/bin/bash

# 小说生成器停止脚本
# 用途：停止前端和后端服务

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

echo -e "${BLUE}🛑 小说生成器停止脚本${NC}"
echo "=================================================="

# 停止MongoDB服务
stop_mongodb() {
    echo -e "${YELLOW}🗄️  停止MongoDB服务...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # 通过PID文件停止
    if [ -f "mongodb.pid" ]; then
        MONGO_PID=$(cat mongodb.pid)
        if kill -0 $MONGO_PID 2>/dev/null; then
            kill -TERM $MONGO_PID 2>/dev/null || true
            sleep 3
            # 如果还在运行，强制杀死
            if kill -0 $MONGO_PID 2>/dev/null; then
                kill -9 $MONGO_PID 2>/dev/null || true
            fi
            echo -e "${GREEN}✅ MongoDB服务已停止 (PID: $MONGO_PID)${NC}"
        else
            echo -e "${YELLOW}⚠️ MongoDB进程不存在或已停止${NC}"
        fi
        rm -f mongodb.pid
    fi
    
    # 备用方案：通过端口停止
    MONGO_PIDS=$(lsof -ti :27017 2>/dev/null || true)
    if [ ! -z "$MONGO_PIDS" ]; then
        echo $MONGO_PIDS | xargs kill -TERM 2>/dev/null || true
        sleep 3
        # 强制杀死仍在运行的进程
        MONGO_PIDS=$(lsof -ti :27017 2>/dev/null || true)
        if [ ! -z "$MONGO_PIDS" ]; then
            echo $MONGO_PIDS | xargs kill -9 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ MongoDB端口27017已清理${NC}"
    fi
}

# 停止后端服务
stop_backend() {
    echo -e "${YELLOW}🔧 停止后端服务...${NC}"
    
    cd "$BACKEND_DIR"
    
    # 通过PID文件停止
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -TERM $BACKEND_PID 2>/dev/null || true
            sleep 2
            # 如果还在运行，强制杀死
            if kill -0 $BACKEND_PID 2>/dev/null; then
                kill -9 $BACKEND_PID 2>/dev/null || true
            fi
            echo -e "${GREEN}✅ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
        else
            echo -e "${YELLOW}⚠️ 后端进程不存在或已停止${NC}"
        fi
        rm -f backend.pid
    fi
    
    # 备用方案：通过端口停止
    BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null || true)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo $BACKEND_PIDS | xargs kill -TERM 2>/dev/null || true
        sleep 2
        # 强制杀死仍在运行的进程
        BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null || true)
        if [ ! -z "$BACKEND_PIDS" ]; then
            echo $BACKEND_PIDS | xargs kill -9 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ 后端端口8000已清理${NC}"
    fi
}

# 停止前端服务
stop_frontend() {
    echo -e "${YELLOW}🌐 停止前端服务...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 通过PID文件停止
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill -TERM $FRONTEND_PID 2>/dev/null || true
            sleep 2
            # 如果还在运行，强制杀死
            if kill -0 $FRONTEND_PID 2>/dev/null; then
                kill -9 $FRONTEND_PID 2>/dev/null || true
            fi
            echo -e "${GREEN}✅ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
        else
            echo -e "${YELLOW}⚠️ 前端进程不存在或已停止${NC}"
        fi
        rm -f frontend.pid
    fi
    
    # 备用方案：通过端口停止
    FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null || true)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo $FRONTEND_PIDS | xargs kill -TERM 2>/dev/null || true
        sleep 2
        # 强制杀死仍在运行的进程
        FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null || true)
        if [ ! -z "$FRONTEND_PIDS" ]; then
            echo $FRONTEND_PIDS | xargs kill -9 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ 前端端口3000已清理${NC}"
    fi
}

# 清理临时文件
cleanup() {
    echo -e "${YELLOW}🧹 清理临时文件...${NC}"
    
    # 删除日志文件（可选）
    if [ "$1" = "--clean-logs" ]; then
        rm -f "$PROJECT_ROOT/mongodb.log"
        rm -f "$BACKEND_DIR/backend.log"
        rm -f "$FRONTEND_DIR/frontend.log"
        echo -e "${GREEN}✅ 日志文件已清理${NC}"
    fi
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 显示状态
show_status() {
    echo ""
    echo "=================================================="
    echo -e "${GREEN}✅ 小说生成器已停止${NC}"
    echo ""
    echo -e "${BLUE}🔍 端口状态检查：${NC}"
    
    # 检查端口状态
    if lsof -i :27017 &>/dev/null; then
        echo -e "  🗄️  端口27017: ${RED}仍被占用${NC}"
    else
        echo -e "  🗄️  端口27017: ${GREEN}已释放${NC}"
    fi
    
    if lsof -i :8000 &>/dev/null; then
        echo -e "  🔧 端口8000: ${RED}仍被占用${NC}"
    else
        echo -e "  🔧 端口8000: ${GREEN}已释放${NC}"
    fi
    
    if lsof -i :3000 &>/dev/null; then
        echo -e "  🌐 端口3000: ${RED}仍被占用${NC}"
    else
        echo -e "  🌐 端口3000: ${GREEN}已释放${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📝 重新启动：${NC}"
    echo -e "  启动服务:   ./start.sh"
    echo "=================================================="
}

# 主函数
main() {
    stop_frontend
    stop_backend
    stop_mongodb
    cleanup "$@"
    show_status
}

# 运行主函数
main "$@"
