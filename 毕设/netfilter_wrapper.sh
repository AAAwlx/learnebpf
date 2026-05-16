#!/bin/bash
# netfilter_trace 交互式包装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置文件
LOG_DIR="./logs"
LOG_FILE="${LOG_DIR}/netfilter_trace_$(date +%Y%m%d_%H%M%S).log"
BPFTRACE_SCRIPT="./netfilter_trace.bt"

# 过滤条件（初始化为空）
FILTER_IP=""
FILTER_HOOK=""
FILTER_RESULT=""
FILTER_SKB=""
LOG_MODE=false
FILTER_ENABLED=false

# 创建日志目录
mkdir -p "$LOG_DIR"

# 打印标题
print_header() {
    clear
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${CYAN}     Netfilter Trace - 交互式过滤工具${NC}"
    echo -e "${CYAN}==========================================${NC}"
    echo ""
}

# 打印当前配置
print_config() {
    echo -e "${BLUE}当前配置：${NC}"
    echo "----------------------------------------"

    if [ -n "$FILTER_IP" ]; then
        echo -e "  ${GREEN}✓${NC} IP 过滤: ${FILTER_IP}"
    else
        echo -e "  ${GRAY}  IP 过滤: 未设置${NC}"
    fi

    if [ -n "$FILTER_HOOK" ]; then
        echo -e "  ${GREEN}✓${NC} Hook 过滤: ${FILTER_HOOK}"
    else
        echo -e "  ${GRAY}  Hook 过滤: 未设置${NC}"
    fi

    if [ -n "$FILTER_RESULT" ]; then
        echo -e "  ${GREEN}✓${NC} 结果过滤: ${FILTER_RESULT}"
    else
        echo -e "  ${GRAY}  结果过滤: 未设置${NC}"
    fi

    if [ -n "$FILTER_SKB" ]; then
        echo -e "  ${GREEN}✓${NC} SKB 过滤: ${FILTER_SKB}"
    else
        echo -e "  ${GRAY}  SKB 过滤: 未设置${NC}"
    fi

    if [ "$LOG_MODE" = true ]; then
        echo -e "  ${GREEN}✓${NC} 日志模式: ${YELLOW}开启${NC} → ${LOG_FILE}"
    else
        echo -e "  ${GREEN}✓${NC} 日志模式: ${YELLOW}关闭${NC}"
    fi

    echo "----------------------------------------"
    echo ""
}

# 生成过滤命令
generate_filter() {
    local filter_cmd="cat"

    # 如果没有启用任何过滤，返回 cat（全量输出）
    if [ "$FILTER_ENABLED" = false ]; then
        echo "cat"
        return
    fi

    # 构建 grep 过滤链
    if [ -n "$FILTER_IP" ]; then
        filter_cmd="${filter_cmd} | grep '${FILTER_IP}'"
    fi

    if [ -n "$FILTER_HOOK" ]; then
        filter_cmd="${filter_cmd} | grep 'hook_num:${FILTER_HOOK}'"
    fi

    if [ -n "$FILTER_RESULT" ]; then
        if [ "$FILTER_RESULT" = "ACCEPT" ]; then
            filter_cmd="${filter_cmd} | grep '\[ACCEPT\]'"
        elif [ "$FILTER_RESULT" = "DROP" ]; then
            filter_cmd="${filter_cmd} | grep '\[DROP\]'"
        elif [ "$FILTER_RESULT" = "OTHER" ]; then
            filter_cmd="${filter_cmd} | grep -v '\[ACCEPT\]' | grep -v '\[DROP\]'"
        fi
    fi

    if [ -n "$FILTER_SKB" ]; then
        filter_cmd="${filter_cmd} | grep 'skb:${FILTER_SKB}'"
    fi

    echo "$filter_cmd"
}

# 主菜单
show_menu() {
    print_header
    print_config

    echo -e "${GREEN}过滤选项：${NC}"
    echo "  1. 按 IP 地址过滤"
    echo "  2. 按 Hook 编号过滤"
    echo "  3. 按处理结果过滤 (ACCEPT/DROP/OTHER)"
    echo "  4. 按 SKB 地址过滤"
    echo ""
    echo -e "${GREEN}日志选项：${NC}"
    echo "  5. 切换日志模式 (当前: $([ "$LOG_MODE" = true ] && echo '开启' || echo '关闭'))"
    echo ""
    echo -e "${GREEN}操作：${NC}"
    echo "  6. 清除所有过滤条件"
    echo "  7. 开始监控"
    echo -e "  ${CYAN}8. AI 智能分析模式${NC}"
    echo "  9. 退出"
    echo ""
    echo -ne "${YELLOW}请选择 [1-9]: ${NC}"
}

# 设置 IP 过滤
set_ip_filter() {
    echo ""
    echo -e "${CYAN}设置 IP 过滤${NC}"
    echo "示例: 192.168.1.1, 8.8.8.8"
    echo -ne "请输入 IP 地址 (留空清除): "
    read -r ip

    if [ -z "$ip" ]; then
        FILTER_IP=""
        FILTER_ENABLED=false
    else
        FILTER_IP="$ip"
        FILTER_ENABLED=true
        echo -e "${GREEN}✓ 已设置 IP 过滤: $ip${NC}"
    fi

    check_filters
    sleep 1
}

# 设置 Hook 过滤
set_hook_filter() {
    echo ""
    echo -e "${CYAN}设置 Hook 编号过滤${NC}"
    echo "常用 Hook 编号:"
    echo "  0  - NF_INET_PRE_ROUTING"
    echo "  1  - NF_INET_LOCAL_IN"
    echo "  2  - NF_INET_FORWARD"
    echo "  3  - NF_INET_LOCAL_OUT"
    echo "  4  - NF_INET_POST_ROUTING"
    echo ""
    echo -ne "请输入 Hook 编号 (0-4, 留空清除): "
    read -r hook

    if [ -z "$hook" ]; then
        FILTER_HOOK=""
        FILTER_ENABLED=false
    else
        if [[ "$hook" =~ ^[0-4]$ ]]; then
            FILTER_HOOK="$hook"
            FILTER_ENABLED=true
            echo -e "${GREEN}✓ 已设置 Hook 过滤: $hook${NC}"
        else
            echo -e "${RED}✗ 无效的 Hook 编号${NC}"
            sleep 1
        fi
    fi

    check_filters
    sleep 1
}

# 设置结果过滤
set_result_filter() {
    echo ""
    echo -e "${CYAN}设置处理结果过滤${NC}"
    echo "  1. ACCEPT (接受)"
    echo "  2. DROP   (丢弃)"
    echo "  3. OTHER  (其他)"
    echo ""
    echo -ne "请选择结果类型 [1-3, 留空清除]: "
    read -r choice

    case "$choice" in
        1)
            FILTER_RESULT="ACCEPT"
            FILTER_ENABLED=true
            echo -e "${GREEN}✓ 已设置为过滤 ACCEPT${NC}"
            ;;
        2)
            FILTER_RESULT="DROP"
            FILTER_ENABLED=true
            echo -e "${GREEN}✓ 已设置为过滤 DROP${NC}"
            ;;
        3)
            FILTER_RESULT="OTHER"
            FILTER_ENABLED=true
            echo -e "${GREEN}✓ 已设置为过滤 OTHER${NC}"
            ;;
        "")
            FILTER_RESULT=""
            FILTER_ENABLED=false
            ;;
        *)
            echo -e "${RED}✗ 无效的选择${NC}"
            sleep 1
            ;;
    esac

    check_filters
    sleep 1
}

# 设置 SKB 过滤
set_skb_filter() {
    echo ""
    echo -e "${CYAN}设置 SKB 地址过滤${NC}"
    echo "示例: ffff888123456789 (无需 0x 前缀)"
    echo -ne "请输入 SKB 地址 (留空清除): "
    read -r skb

    if [ -z "$skb" ]; then
        FILTER_SKB=""
        FILTER_ENABLED=false
    else
        FILTER_SKB="$skb"
        FILTER_ENABLED=true
        echo -e "${GREEN}✓ 已设置 SKB 过滤: $skb${NC}"
    fi

    check_filters
    sleep 1
}

# 切换日志模式
toggle_log_mode() {
    if [ "$LOG_MODE" = true ]; then
        LOG_MODE=false
        echo -e "${YELLOW}日志模式已关闭${NC}"
    else
        LOG_MODE=true
        echo -e "${GREEN}日志模式已开启 → ${LOG_FILE}${NC}"
    fi
    sleep 1
}

# 清除所有过滤
clear_all_filters() {
    FILTER_IP=""
    FILTER_HOOK=""
    FILTER_RESULT=""
    FILTER_SKB=""
    FILTER_ENABLED=false
    echo -e "${GREEN}✓ 所有过滤条件已清除${NC}"
    sleep 1
}

# 检查是否有任何过滤条件
check_filters() {
    if [ -z "$FILTER_IP" ] && [ -z "$FILTER_HOOK" ] && [ -z "$FILTER_RESULT" ] && [ -z "$FILTER_SKB" ]; then
        FILTER_ENABLED=false
    fi
}

# AI 分析模式
start_ai_analysis() {
    clear
    print_header

    echo -e "${CYAN}🤖 AI 智能分析模式${NC}"
    echo "========================================"
    echo ""

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到 python3${NC}"
        echo "请先安装 Python 3"
        exit 1
    fi

    # 检查分析器脚本
    ANALYZER="./netfilter_analyzer.py"
    if [ ! -f "$ANALYZER" ]; then
        echo -e "${RED}错误: 未找到 ${ANALYZER}${NC}"
        exit 1
    fi

    # AI 分析选项
    echo -e "${GREEN}分析模式选择：${NC}"
    echo "  1. 本地分析（快速，无需 API）"
    echo "  2. AI 深度分析（需要 Anthropic API Key）"
    echo ""
    echo -ne "${YELLOW}请选择 [1-2]: ${NC}"
    read -r ai_choice

    API_KEY=""
    if [ "$ai_choice" = "2" ]; then
        echo ""
        echo -e "${CYAN}配置 AI API${NC}"
        echo "提示: 可以设置环境变量 ANTHROPIC_API_KEY"
        echo ""

        # 尝试从环境变量获取
        if [ -n "$ANTHROPIC_API_KEY" ]; then
            echo -e "${GREEN}✓ 检测到环境变量中的 API Key${NC}"
            API_KEY="$ANTHROPIC_API_KEY"
        else
            echo -ne "请输入 Anthropic API Key (留空跳转本地分析): "
            read -r -s API_KEY
            echo ""

            if [ -z "$API_KEY" ]; then
                echo -e "${YELLOW}未提供 API Key，切换到本地分析模式${NC}"
                ai_choice="1"
            fi
        fi
    fi

    # 报告间隔
    echo ""
    echo -ne "请输入报告生成间隔（秒，默认30）: "
    read -r interval
    interval=${interval:-30}

    echo ""
    echo -e "${GREEN}启动 AI 监控与分析...${NC}"
    echo ""

    # 显示当前配置
    print_config

    if [ "$FILTER_ENABLED" = true ]; then
        echo -e "${YELLOW}⚠️  过滤模式已启用，AI将分析过滤后的数据${NC}"
    else
        echo -e "${YELLOW}全量分析模式${NC}"
    fi

    echo ""
    echo -e "${CYAN}分析设置：${NC}"
    if [ "$ai_choice" = "2" ]; then
        echo "  模式: AI 深度分析"
        echo "  API: Anthropic Claude"
    else
        echo "  模式: 本地统计分析"
    fi
    echo "  间隔: ${interval} 秒"

    echo ""
    echo -e "${CYAN}按 Ctrl+C 查看最终报告并退出${NC}"
    echo "========================================"
    echo ""

    # 检查 bpftrace
    if ! command -v bpftrace &> /dev/null; then
        echo -e "${RED}错误: 未找到 bpftrace${NC}"
        echo "请先安装: sudo apt install bpftrace"
        exit 1
    fi

    # 生成过滤命令
    local filter_cmd=$(generate_filter)

    # 构建分析器命令
    if [ "$ai_choice" = "2" ] && [ -n "$API_KEY" ]; then
        analyzer_cmd="python3 $ANALYZER --mode stream --interval $interval --api-key '$API_KEY'"
    else
        analyzer_cmd="python3 $ANALYZER --mode stream --interval $interval"
    fi

    # 启动监控管道
    {
        if [ "$FILTER_ENABLED" = true ]; then
            # 过滤模式
            sudo bpftrace "$BPFTRACE_SCRIPT" 2>/dev/null | eval "$filter_cmd"
        else
            # 全量模式
            sudo bpftrace "$BPFTRACE_SCRIPT" 2>/dev/null
        fi
    } | eval "$analyzer_cmd"
}

# 开始监控
start_monitoring() {
    clear
    print_header

    echo -e "${GREEN}启动 netfilter trace 监控...${NC}"
    echo ""

    # 检查 bpftrace
    if ! command -v bpftrace &> /dev/null; then
        echo -e "${RED}错误: 未找到 bpftrace${NC}"
        echo "请先安装: sudo apt install bpftrace"
        exit 1
    fi

    # 检查脚本
    if [ ! -f "$BPFTRACE_SCRIPT" ]; then
        echo -e "${RED}错误: 未找到 ${BPFTRACE_SCRIPT}${NC}"
        exit 1
    fi

    # 显示当前配置
    print_config

    if [ "$FILTER_ENABLED" = true ]; then
        echo -e "${YELLOW}过滤模式已启用${NC}"
    else
        echo -e "${YELLOW}全量输出模式（未设置过滤条件）${NC}"
    fi

    echo ""
    echo -e "${CYAN}按 Ctrl+C 停止监控${NC}"
    echo "========================================"
    echo ""

    # 生成过滤命令
    local filter_cmd=$(generate_filter)

    # 启动监控
    if [ "$LOG_MODE" = true ]; then
        echo -e "${GREEN}写入日志: ${LOG_FILE}${NC}"
        echo ""

        # 日志模式：同时输出到屏幕和日志文件
        if [ "$FILTER_ENABLED" = true ]; then
            # 过滤 + 日志
            sudo bpftrace "$BPFTRACE_SCRIPT" 2>/dev/null | eval "$filter_cmd" | tee -a "$LOG_FILE"
        else
            # 全量 + 日志
            sudo bpftrace "$BPFTRACE_SCRIPT" 2>/dev/null | tee -a "$LOG_FILE"
        fi
    else
        # 非日志模式：仅输出到屏幕
        if [ "$FILTER_ENABLED" = true ]; then
            # 过滤输出
            sudo bpftrace "$BPFTRACE_SCRIPT" 2>/dev/null | eval "$filter_cmd"
        else
            # 全量输出
            sudo bpftrace "$BPFTRACE_SCRIPT" 2>/dev/null
        fi
    fi
}

# 主循环
main() {
    while true; do
        show_menu
        read -r choice

        case "$choice" in
            1)
                set_ip_filter
                ;;
            2)
                set_hook_filter
                ;;
            3)
                set_result_filter
                ;;
            4)
                set_skb_filter
                ;;
            5)
                toggle_log_mode
                ;;
            6)
                clear_all_filters
                ;;
            7)
                start_monitoring
                ;;
            8)
                start_ai_analysis
                ;;
            9)
                echo ""
                echo -e "${GREEN}再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效的选择，请重试${NC}"
                sleep 1
                ;;
        esac
    done
}

# 启动
main
