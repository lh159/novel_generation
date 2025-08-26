#!/bin/bash

# 小说生成器重启脚本
# 用途：安全重启所有服务，包含完整的状态检查和错误处理

set -euo pipefail  # 严格错误处理

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m' # No Color

# 配置常量
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly STOP_SCRIPT="$PROJECT_ROOT/stop.sh"
readonly START_SCRIPT="$PROJECT_ROOT/start.sh"
readonly MAX_RETRY_ATTEMPTS=3
readonly WAIT_BETWEEN_RETRIES=5

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

log_highlight() {
    echo -e "${MAGENTA}🎯 $1${NC}"
}

# 检查脚本是否存在且可执行
check_script() {
    local script_path=$1
    local script_name=$(basename "$script_path")
    
    if [ ! -f "$script_path" ]; then
        log_error "$script_name 脚本不存在: $script_path"
        return 1
    fi
    
    if [ ! -x "$script_path" ]; then
        log_warning "$script_name 脚本不可执行，正在设置权限..."
        if chmod +x "$script_path"; then
            log_success "$script_name 脚本权限已设置"
        else
            log_error "无法设置 $script_name 脚本权限"
            return 1
        fi
    fi
    
    return 0
}

# 检查端口状态
check_ports() {
    local ports=("3000" "8000" "27017")
    local port_status=()
    
    for port in "${ports[@]}"; do
        if lsof -i ":$port" &>/dev/null; then
            port_status+=("$port:occupied")
        else
            port_status+=("$port:free")
        fi
    done
    
    echo "${port_status[@]}"
}

# 显示端口状态
show_port_status() {
    local title=$1
    local port_status=($(check_ports))
    
    echo -e "${BLUE}🔍 $title 端口状态：${NC}"
    
    for status in "${port_status[@]}"; do
        local port=$(echo "$status" | cut -d':' -f1)
        local state=$(echo "$status" | cut -d':' -f2)
        
        case $port in
            "3000") local icon="🌐"; local name="前端" ;;
            "8000") local icon="🔧"; local name="后端" ;;
            "27017") local icon="🗄️"; local name="MongoDB" ;;
        esac
        
        if [ "$state" = "occupied" ]; then
            echo -e "  $icon $name (端口$port): ${RED}占用中${NC}"
        else
            echo -e "  $icon $name (端口$port): ${GREEN}空闲${NC}"
        fi
    done
}

# 执行停止脚本
execute_stop() {
    local clean_option=$1
    
    log_step "执行停止脚本..."
    
    if [ -n "$clean_option" ]; then
        log_info "使用清理选项: $clean_option"
        if "$STOP_SCRIPT" "$clean_option"; then
            log_success "停止脚本执行成功"
            return 0
        else
            log_error "停止脚本执行失败"
            return 1
        fi
    else
        if "$STOP_SCRIPT"; then
            log_success "停止脚本执行成功"
            return 0
        else
            log_error "停止脚本执行失败"
            return 1
        fi
    fi
}

# 执行启动脚本
execute_start() {
    log_step "执行启动脚本..."
    
    if "$START_SCRIPT"; then
        log_success "启动脚本执行成功"
        return 0
    else
        log_error "启动脚本执行失败"
        return 1
    fi
}

# 等待系统稳定
wait_for_stability() {
    local wait_time=$1
    local reason="${2:-系统稳定}"
    
    log_info "${reason}，等待 ${wait_time} 秒..."
    
    for i in $(seq 1 $wait_time); do
        echo -ne "\r⏳ 等待中... (${i}/${wait_time}s)"
        sleep 1
    done
    echo ""
    log_success "等待完成"
}

# 验证服务状态
verify_services() {
    log_step "验证服务状态..."
    
    local all_running=true
    local services=("mongodb" "backend" "frontend")
    
    for service in "${services[@]}"; do
        local service_info=$(get_service_info "$service")
        local port=$(echo "$service_info" | cut -d':' -f1)
        local display_name=$(echo "$service_info" | cut -d':' -f4)
        
        if lsof -i ":$port" &>/dev/null; then
            log_success "$display_name 服务正在运行 (端口:$port)"
        else
            log_warning "$display_name 服务可能未正常启动 (端口:$port)"
            all_running=false
        fi
    done
    
    if $all_running; then
        return 0
    else
        return 1
    fi
}

# 获取服务信息（与stop.sh保持一致）
get_service_info() {
    local service_name=$1
    
    case $service_name in
        "frontend")
            echo "3000:$PROJECT_ROOT/frontend/frontend.pid:🌐:前端"
            ;;
        "backend")
            echo "8000:$PROJECT_ROOT/backend/backend.pid:🔧:后端"
            ;;
        "mongodb")
            echo "27017:$PROJECT_ROOT/mongodb.pid:🗄️:MongoDB"
            ;;
        *)
            echo "unknown:unknown:❓:未知"
            ;;
    esac
}

# 重启失败处理
handle_restart_failure() {
    local attempt=$1
    local max_attempts=$2
    
    log_error "重启尝试 $attempt/$max_attempts 失败"
    
    if [ $attempt -lt $max_attempts ]; then
        log_warning "等待 $WAIT_BETWEEN_RETRIES 秒后重试..."
        wait_for_stability $WAIT_BETWEEN_RETRIES "重试前稳定系统"
        return 0  # 继续重试
    else
        log_error "已达到最大重试次数，重启失败"
        
        echo ""
        echo -e "${RED}🚨 重启失败诊断：${NC}"
        echo -e "${YELLOW}1. 检查错误日志：${NC}"
        echo -e "   ./logs.sh"
        echo -e "${YELLOW}2. 手动停止所有进程：${NC}"
        echo -e "   ./stop.sh --clean-all"
        echo -e "${YELLOW}3. 检查端口占用：${NC}"
        echo -e "   lsof -i :3000,8000,27017"
        echo -e "${YELLOW}4. 重新启动：${NC}"
        echo -e "   ./start.sh"
        
        return 1  # 终止重试
    fi
}

# 显示重启结果
show_results() {
    local success=$1
    
    echo ""
    echo "=================================================="
    
    if $success; then
        echo -e "${GREEN}🎉 小说生成器重启成功！${NC}"
        echo ""
        echo -e "${BLUE}📊 服务地址：${NC}"
        echo -e "  🗄️  MongoDB:   ${CYAN}mongodb://localhost:27017${NC}"
        echo -e "  🔧 后端API:  ${CYAN}http://localhost:8000${NC}"
        echo -e "  🌐 前端界面: ${CYAN}http://localhost:3000${NC}"
        
        echo ""
        echo -e "${BLUE}📝 管理命令：${NC}"
        echo -e "  停止服务:   ${CYAN}./stop.sh${NC}"
        echo -e "  查看日志:   ${CYAN}./logs.sh${NC}"
        echo -e "  重新重启:   ${CYAN}./restart.sh${NC}"
    else
        echo -e "${RED}💥 小说生成器重启失败${NC}"
        echo ""
        echo -e "${YELLOW}📝 故障排除：${NC}"
        echo -e "  检查日志:   ${CYAN}./logs.sh${NC}"
        echo -e "  强制停止:   ${CYAN}./stop.sh --clean-all${NC}"
        echo -e "  手动启动:   ${CYAN}./start.sh${NC}"
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
    local clean_option=""
    local force_restart=false
    local skip_verification=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean-logs)
                clean_option="--clean-logs"
                shift
                ;;
            --clean-cache)
                clean_option="--clean-cache"
                shift
                ;;
            --clean-all)
                clean_option="--clean-all"
                shift
                ;;
            --force)
                force_restart=true
                shift
                ;;
            --skip-verification)
                skip_verification=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo -e "${BLUE}🔄 小说生成器重启脚本${NC}"
    echo "=================================================="
    
    # 检查必要脚本
    log_step "检查脚本依赖..."
    if ! check_script "$STOP_SCRIPT" || ! check_script "$START_SCRIPT"; then
        log_error "脚本依赖检查失败"
        exit 1
    fi
    log_success "脚本依赖检查通过"
    echo ""
    
    # 显示重启前状态
    show_port_status "重启前"
    echo ""
    
    # 重启循环
    local success=false
    for attempt in $(seq 1 $MAX_RETRY_ATTEMPTS); do
        if [ $attempt -gt 1 ]; then
            log_highlight "重启尝试 $attempt/$MAX_RETRY_ATTEMPTS"
            echo ""
        fi
        
        # 停止服务
        log_highlight "步骤 1/3: 停止现有服务"
        if execute_stop "$clean_option"; then
            wait_for_stability 3 "确保服务完全停止"
            echo ""
            
            # 启动服务
            log_highlight "步骤 2/3: 启动所有服务"
            if execute_start; then
                wait_for_stability 5 "等待服务初始化"
                echo ""
                
                # 验证服务
                if ! $skip_verification; then
                    log_highlight "步骤 3/3: 验证服务状态"
                    if verify_services; then
                        success=true
                        break
                    else
                        log_warning "服务验证失败"
                    fi
                else
                    log_info "跳过服务验证"
                    success=true
                    break
                fi
            else
                log_error "启动服务失败"
            fi
        else
            log_error "停止服务失败"
        fi
        
        # 处理失败情况
        if ! handle_restart_failure $attempt $MAX_RETRY_ATTEMPTS; then
            break
        fi
        echo ""
    done
    
    echo ""
    # 显示重启后状态
    show_port_status "重启后"
    
    # 显示结果
    show_results $success
    
    if $success; then
        exit 0
    else
        exit 1
    fi
}

# 帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --clean-logs         重启时清理日志文件"
    echo "  --clean-cache        重启时清理缓存文件" 
    echo "  --clean-all          重启时清理所有临时文件"
    echo "  --force              强制重启（忽略当前状态）"
    echo "  --skip-verification  跳过服务验证"
    echo "  --help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                      # 正常重启"
    echo "  $0 --clean-logs         # 重启并清理日志"
    echo "  $0 --clean-all --force  # 强制重启并清理所有文件"
    echo "  $0 --skip-verification  # 快速重启（跳过验证）"
}

# 运行主函数
main "$@"