#!/bin/bash

# 小说生成器重启脚本
# 用途：重启前端和后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 小说生成器重启脚本${NC}"
echo "=================================================="

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}🛑 正在停止现有服务...${NC}"
"$PROJECT_ROOT/stop.sh"

echo ""
echo -e "${YELLOW}⏳ 等待2秒...${NC}"
sleep 2

echo ""
echo -e "${YELLOW}🚀 重新启动服务...${NC}"
"$PROJECT_ROOT/start.sh"
