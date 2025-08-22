#!/bin/bash

# 小说生成器日志查看脚本
# 用途：查看前端、后端和MongoDB服务的日志

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

echo -e "${BLUE}📋 小说生成器日志查看${NC}"
echo "=================================================="

# 显示帮助信息
show_help() {
    echo -e "${YELLOW}使用方法：${NC}"
    echo "  ./logs.sh [选项] [服务名]"
    echo ""
    echo -e "${YELLOW}选项：${NC}"
    echo "  -f, --follow    实时跟踪日志"
    echo "  -n, --lines N   显示最后N行日志（默认50行）"
    echo "  -h, --help      显示此帮助信息"
    echo ""
    echo -e "${YELLOW}服务名：${NC}"
    echo "  mongodb         MongoDB数据库日志"
    echo "  backend         后端API日志"
    echo "  frontend        前端开发服务器日志"
    echo "  all             所有服务日志（默认）"
    echo ""
    echo -e "${YELLOW}示例：${NC}"
    echo "  ./logs.sh                    # 显示所有服务最后50行日志"
    echo "  ./logs.sh -f backend         # 实时跟踪后端日志"
    echo "  ./logs.sh -n 100 mongodb     # 显示MongoDB最后100行日志"
}

# 查看MongoDB日志
show_mongodb_logs() {
    local follow_flag="$1"
    local lines="$2"
    
    echo -e "${YELLOW}🗄️  MongoDB日志：${NC}"
    echo "=================================================="
    
    if [ -f "$PROJECT_ROOT/mongodb.log" ]; then
        if [ "$follow_flag" = "true" ]; then
            tail -f "$PROJECT_ROOT/mongodb.log"
        else
            tail -n "$lines" "$PROJECT_ROOT/mongodb.log"
        fi
    else
        echo -e "${RED}❌ MongoDB日志文件不存在${NC}"
    fi
    echo ""
}

# 查看后端日志
show_backend_logs() {
    local follow_flag="$1"
    local lines="$2"
    
    echo -e "${YELLOW}🔧 后端API日志：${NC}"
    echo "=================================================="
    
    if [ -f "$BACKEND_DIR/backend.log" ]; then
        if [ "$follow_flag" = "true" ]; then
            tail -f "$BACKEND_DIR/backend.log"
        else
            tail -n "$lines" "$BACKEND_DIR/backend.log"
        fi
    else
        echo -e "${RED}❌ 后端日志文件不存在${NC}"
    fi
    echo ""
}

# 查看前端日志
show_frontend_logs() {
    local follow_flag="$1"
    local lines="$2"
    
    echo -e "${YELLOW}🌐 前端开发服务器日志：${NC}"
    echo "=================================================="
    
    if [ -f "$FRONTEND_DIR/frontend.log" ]; then
        if [ "$follow_flag" = "true" ]; then
            tail -f "$FRONTEND_DIR/frontend.log"
        else
            tail -n "$lines" "$FRONTEND_DIR/frontend.log"
        fi
    else
        echo -e "${RED}❌ 前端日志文件不存在${NC}"
    fi
    echo ""
}

# 查看所有日志
show_all_logs() {
    local follow_flag="$1"
    local lines="$2"
    
    if [ "$follow_flag" = "true" ]; then
        echo -e "${YELLOW}📋 实时跟踪所有服务日志（按Ctrl+C停止）：${NC}"
        echo "=================================================="
        
        # 使用multitail或者简单的tail组合
        if command -v multitail &> /dev/null; then
            multitail -l "tail -f $PROJECT_ROOT/mongodb.log" \
                     -l "tail -f $BACKEND_DIR/backend.log" \
                     -l "tail -f $FRONTEND_DIR/frontend.log"
        else
            echo -e "${YELLOW}💡 提示：安装multitail可获得更好的多日志查看体验${NC}"
            echo -e "${YELLOW}   macOS: brew install multitail${NC}"
            echo -e "${YELLOW}   Ubuntu: sudo apt-get install multitail${NC}"
            echo ""
            
            # 简单的并行tail
            tail -f "$PROJECT_ROOT/mongodb.log" &
            MONGO_TAIL_PID=$!
            tail -f "$BACKEND_DIR/backend.log" &
            BACKEND_TAIL_PID=$!
            tail -f "$FRONTEND_DIR/frontend.log" &
            FRONTEND_TAIL_PID=$!
            
            # 捕获中断信号并清理
            trap 'kill $MONGO_TAIL_PID $BACKEND_TAIL_PID $FRONTEND_TAIL_PID 2>/dev/null; exit 0' INT TERM
            
            wait
        fi
    else
        show_mongodb_logs "$follow_flag" "$lines"
        show_backend_logs "$follow_flag" "$lines"
        show_frontend_logs "$follow_flag" "$lines"
    fi
}

# 解析命令行参数
FOLLOW_FLAG="false"
LINES="50"
SERVICE="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW_FLAG="true"
            shift
            ;;
        -n|--lines)
            LINES="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        mongodb|backend|frontend|all)
            SERVICE="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ 未知参数: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 验证lines参数
if ! [[ "$LINES" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}❌ 行数必须是正整数${NC}"
    exit 1
fi

# 根据服务名显示对应日志
case $SERVICE in
    mongodb)
        show_mongodb_logs "$FOLLOW_FLAG" "$LINES"
        ;;
    backend)
        show_backend_logs "$FOLLOW_FLAG" "$LINES"
        ;;
    frontend)
        show_frontend_logs "$FOLLOW_FLAG" "$LINES"
        ;;
    all)
        show_all_logs "$FOLLOW_FLAG" "$LINES"
        ;;
    *)
        echo -e "${RED}❌ 未知服务: $SERVICE${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}✅ 日志查看完成${NC}"