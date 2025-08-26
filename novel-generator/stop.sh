#!/bin/bash

# 小说生成器停止脚本
# 用途：安全停止所有服务，包含完整的错误处理和状态检查

set -euo pipefail  # 严格错误处理

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# 配置常量
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BACKEND_DIR="$PROJECT_ROOT/backend"
readonly FRONTEND_DIR="$PROJECT_ROOT/frontend"
readonly TIMEOUT_GRACEFUL=10  # 优雅停止超时时间(秒)
readonly TIMEOUT_FORCE=5      # 强制停止超时时间(秒)

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${CYAN}📍 $1${NC}"
}

# 获取服务信息
get_service_info() {
    local service_name=$1
    
    case $service_name in
        "frontend")
            echo "3000:$FRONTEND_DIR/frontend.pid:🌐:前端"
            ;;
        "backend")
            echo "8000:$BACKEND_DIR/backend.pid:🔧:后端"
            ;;
        "mongodb")
            echo "27017:$PROJECT_ROOT/mongodb.pid:🗄️:MongoDB"
            ;;
        *)
            echo "unknown:unknown:❓:未知"
            ;;
    esac
}

# 检查进程是否运行
is_process_running() {
    local pid=$1
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

# 等待进程停止
wait_for_process_stop() {
    local pid=$1
    local timeout=$2
    local service_name=$3
    
    for i in $(seq 1 $timeout); do
        if ! is_process_running "$pid"; then
            return 0
        fi
        echo -ne "\r⏳ 等待 $service_name 停止... (${i}/${timeout}s)"
        sleep 1
    done
    echo ""
    return 1
}

# 获取端口占用的进程
get_port_pids() {
    local port=$1
    lsof -ti ":$port" 2>/dev/null || true
}

# 停止单个服务
stop_service() {
    local service_name=$1
    local service_info=$(get_service_info "$service_name")
    local port=$(echo "$service_info" | cut -d':' -f1)
    local pid_file=$(echo "$service_info" | cut -d':' -f2)
    local icon=$(echo "$service_info" | cut -d':' -f3)
    local display_name=$(echo "$service_info" | cut -d':' -f4)
    
    log_step "停止${icon} ${display_name}服务..."
    
    local stopped=false
    local pid=""
    
    # 方法1: 通过PID文件停止
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file" 2>/dev/null || true)
        if [ -n "$pid" ] && is_process_running "$pid"; then
            log_info "通过PID文件停止进程 $pid"
            
            # 优雅停止
            if kill -TERM "$pid" 2>/dev/null; then
                if wait_for_process_stop "$pid" $TIMEOUT_GRACEFUL "$display_name"; then
                    log_success "${display_name}服务已优雅停止 (PID: $pid)"
                    stopped=true
                else
                    log_warning "${display_name}服务未在${TIMEOUT_GRACEFUL}秒内停止，尝试强制停止"
                    if kill -KILL "$pid" 2>/dev/null; then
                        if wait_for_process_stop "$pid" $TIMEOUT_FORCE "$display_name"; then
                            log_success "${display_name}服务已强制停止 (PID: $pid)"
                            stopped=true
                        else
                            log_error "${display_name}服务强制停止失败"
                        fi
                    fi
                fi
            else
                log_warning "无法发送TERM信号给进程 $pid"
            fi
        else
            log_warning "PID文件中的进程 $pid 不存在或已停止"
        fi
        
        # 清理PID文件
        rm -f "$pid_file" 2>/dev/null || true
    else
        log_info "PID文件不存在: $pid_file"
    fi
    
    # 方法2: 通过端口停止剩余进程
    local port_pids=$(get_port_pids "$port")
    if [ -n "$port_pids" ]; then
        log_info "发现端口 $port 上仍有进程: $port_pids"
        
        # 优雅停止
        echo "$port_pids" | xargs -r kill -TERM 2>/dev/null || true
        sleep 3
        
        # 检查是否还有进程
        port_pids=$(get_port_pids "$port")
        if [ -n "$port_pids" ]; then
            log_warning "强制停止端口 $port 上的进程: $port_pids"
            echo "$port_pids" | xargs -r kill -KILL 2>/dev/null || true
            sleep 2
        fi
        
        # 最终检查
        port_pids=$(get_port_pids "$port")
        if [ -z "$port_pids" ]; then
            log_success "${display_name}端口${port}已清理"
            stopped=true
        else
            log_error "${display_name}端口${port}清理失败，仍有进程: $port_pids"
        fi
    elif $stopped; then
        log_success "${display_name}端口${port}已释放"
    else
        log_info "${display_name}服务未运行 (端口${port}空闲)"
    fi
}

# 清理临时文件和资源
cleanup_resources() {
    log_step "清理临时文件和资源..."
    
    local clean_logs=false
    local clean_cache=false
    
    # 检查命令行参数
    for arg in "$@"; do
        case $arg in
            --clean-logs)
                clean_logs=true
                ;;
            --clean-cache)
                clean_cache=true
                ;;
            --clean-all)
                clean_logs=true
                clean_cache=true
                ;;
        esac
    done
    
    # 清理PID文件
    local pid_files=(
        "$PROJECT_ROOT/mongodb.pid"
        "$BACKEND_DIR/backend.pid"
        "$FRONTEND_DIR/frontend.pid"
    )
    
    for pid_file in "${pid_files[@]}"; do
        if [ -f "$pid_file" ]; then
            rm -f "$pid_file" 2>/dev/null || true
        fi
    done
    
    # 清理日志文件
    if $clean_logs; then
        log_info "清理日志文件..."
        local log_files=(
            "$PROJECT_ROOT/mongodb.log"
            "$BACKEND_DIR/backend.log"
            "$FRONTEND_DIR/frontend.log"
            "$PROJECT_ROOT/nohup.out"
        )
        
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                rm -f "$log_file" 2>/dev/null && log_success "已删除: $(basename "$log_file")" || true
            fi
        done
    fi
    
    # 清理缓存
    if $clean_cache; then
        log_info "清理缓存文件..."
        
        # 清理前端缓存
        if [ -d "$FRONTEND_DIR/node_modules/.cache" ]; then
            rm -rf "$FRONTEND_DIR/node_modules/.cache" 2>/dev/null && log_success "已清理前端缓存" || true
        fi
        
        # 清理Python缓存
        find "$BACKEND_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$BACKEND_DIR" -name "*.pyc" -delete 2>/dev/null || true
        log_success "已清理Python缓存"
    fi
    
    log_success "资源清理完成"
}

# 检查系统状态
check_system_status() {
    log_step "检查系统状态..."
    
    local all_stopped=true
    local services=("frontend" "backend" "mongodb")
    
    echo ""
    echo -e "${BLUE}🔍 端口状态检查：${NC}"
    
    for service in "${services[@]}"; do
        local service_info=$(get_service_info "$service")
        local port=$(echo "$service_info" | cut -d':' -f1)
        local icon=$(echo "$service_info" | cut -d':' -f3)
        local display_name=$(echo "$service_info" | cut -d':' -f4)
        
        if lsof -i ":$port" &>/dev/null; then
            echo -e "  ${icon} ${display_name} (端口${port}): ${RED}仍被占用${NC}"
            all_stopped=false
        else
            echo -e "  ${icon} ${display_name} (端口${port}): ${GREEN}已释放${NC}"
        fi
    done
    
    echo ""
    if $all_stopped; then
        echo -e "${BLUE}💾 资源状态：${NC}"
        
        # 检查内存使用
        local memory_info=$(ps aux | grep -E "(mongod|uvicorn|node)" | grep -v grep | awk '{sum+=$6} END {print sum/1024}' 2>/dev/null || echo "0")
        echo -e "  📊 相关进程内存释放: ${GREEN}~${memory_info}MB${NC}"
        
        # 检查磁盘空间
        local disk_usage=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//')
        if [ "$disk_usage" -lt 90 ]; then
            echo -e "  💽 磁盘使用率: ${GREEN}${disk_usage}%${NC}"
        else
            echo -e "  💽 磁盘使用率: ${YELLOW}${disk_usage}%${NC}"
        fi
    fi
    
    if $all_stopped; then
        return 0
    else
        return 1
    fi
}

# 显示停止结果
show_results() {
    local success=$1
    
    echo ""
    echo "=================================================="
    
    if $success; then
        echo -e "${GREEN}✅ 小说生成器已完全停止${NC}"
    else
        echo -e "${YELLOW}⚠️  小说生成器部分停止（存在残留进程）${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📝 可用命令：${NC}"
    echo -e "  重新启动:   ${CYAN}./start.sh${NC}"
    echo -e "  查看日志:   ${CYAN}./logs.sh${NC}"
    echo -e "  强制清理:   ${CYAN}./stop.sh --clean-all${NC}"
    
    if ! $success; then
        echo ""
        echo -e "${YELLOW}💡 如果有进程残留，可以尝试：${NC}"
        echo -e "  1. 等待几秒后重试: ${CYAN}sleep 5 && ./stop.sh${NC}"
        echo -e "  2. 检查具体进程: ${CYAN}lsof -i :3000,8000,27017${NC}"
        echo -e "  3. 手动清理端口: ${CYAN}sudo lsof -ti :端口号 | xargs kill -9${NC}"
    fi
    
    echo "=================================================="
}

# 信号处理
cleanup_on_exit() {
    echo ""
    log_warning "收到中断信号，正在清理..."
    exit 1
}

trap cleanup_on_exit INT TERM

# 主函数
main() {
    echo -e "${BLUE}🛑 小说生成器停止脚本${NC}"
    echo "=================================================="
    
    # 按服务逆序停止（前端->后端->数据库）
    local services_order=("frontend" "backend" "mongodb")
    
    for service in "${services_order[@]}"; do
        stop_service "$service"
        echo ""
    done
    
    # 清理资源
    cleanup_resources "$@"
    echo ""
    
    # 检查状态并显示结果
    if check_system_status; then
        show_results true
        exit 0
    else
        show_results false
        exit 1
    fi
}

# 帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --clean-logs    清理日志文件"
    echo "  --clean-cache   清理缓存文件"
    echo "  --clean-all     清理所有临时文件"
    echo "  --help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 正常停止"
    echo "  $0 --clean-logs      # 停止并清理日志"
    echo "  $0 --clean-all       # 停止并清理所有文件"
}

# 参数处理
if [[ $# -gt 0 && "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# 运行主函数
main "$@"