#!/bin/bash
# 演示助手脚本 - 自动化生成测试流量和常用操作

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  netfilter_trace 演示助手${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 显示帮助信息
show_help() {
    echo "使用方法："
    echo "  $0 [命令]"
    echo ""
    echo "命令："
    echo "  prepare     - 准备演示环境"
    echo "  traffic     - 生成测试流量"
    echo "  mixed       - 生成混合流量"
    echo "  logs        - 显示日志目录"
    echo "  clean       - 清理日志文件"
    echo "  demo        - 运行完整演示流程"
    echo "  help        - 显示此帮助"
    echo ""
}

# 准备环境
prepare_env() {
    echo -e "${GREEN}[1/5] 检查依赖...${NC}"
    command -v bpftrace >/dev/null 2>&1 || { echo "❌ 未安装 bpftrace"; exit 1; }
    echo "✓ bpftrace 已安装"

    echo -e "${GREEN}[2/5] 检查 sudo 权限...${NC}"
    sudo -v >/dev/null 2>&1 || { echo "❌ 需要 sudo 权限"; exit 1; }
    echo "✓ sudo 权限可用"

    echo -e "${GREEN}[3/5] 清理旧日志...${NC}"
    mkdir -p logs
    rm -rf logs/*
    echo "✓ 日志目录已清理"

    echo -e "${GREEN}[4/5] 测试网络连接...${NC}"
    ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "✓ 网络正常" || echo "⚠️  网络可能不可用"

    echo -e "${GREEN}[5/5] 准备完成！${NC}"
    echo ""
    echo "现在可以开始录制演示了！"
    echo ""
}

# 生成基础流量
generate_traffic() {
    echo -e "${YELLOW}生成基础测试流量...${NC}"
    echo ""

    echo "1. DNS 查询 (8.8.8.8)"
    ping -c 3 8.8.8.8
    sleep 1

    echo "2. HTTP 请求 (Google)"
    curl -s -o /dev/null -w "状态码: %{http_code}\n" https://www.google.com --max-time 5 || echo "⚠️  Google 不可用"
    sleep 1

    echo "3. HTTP 请求 (Baidu)"
    curl -s -o /dev/null -w "状态码: %{http_code}\n" https://www.baidu.com --max-time 5 || echo "⚠️  Baidu 不可用"
    sleep 1

    echo "4. 本地连接"
    curl -s -o /dev/null -w "状态码: %{http_code}\n" http://127.0.0.1 --max-time 2 || echo "⚠️  本地无服务"
    sleep 1

    echo "✓ 基础流量生成完成"
    echo ""
}

# 生成混合流量
generate_mixed_traffic() {
    echo -e "${YELLOW}生成混合测试流量...${NC}"
    echo ""

    echo "阶段1: 密集 ICMP 流量"
    for i in {1..5}; do
        echo "  批次 $i/5"
        ping -c 2 8.8.8.8 >/dev/null 2>&1 &
        ping -c 2 1.1.1.1 >/dev/null 2>&1 &
        sleep 0.5
    done
    wait
    sleep 2

    echo "阶段2: HTTP 并发请求"
    echo "  发起10个并发请求..."
    for i in {1..10}; do
        curl -s -o /dev/null https://www.google.com --max-time 3 &
        sleep 0.2
    done
    wait
    sleep 2

    echo "阶段3: 持续流量 (20秒)"
    echo "  运行中..."
    (
        for i in {1..20}; do
            ping -c 1 8.8.8.8 >/dev/null 2>&1 &
            sleep 1
        done
    ) &
    local traffic_pid=$!

    # 倒计时
    for i in {20..1}; do
        echo -ne "\r  剩余: ${i} 秒"
        sleep 1
    done
    echo ""

    wait $traffic_pid

    echo "✓ 混合流量生成完成"
    echo ""
}

# 显示日志
show_logs() {
    echo -e "${YELLOW}日志文件列表：${NC}"
    echo ""

    if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
        ls -lht logs/ | head -10
        echo ""

        local latest=$(ls -t logs/*.log 2>/dev/null | head -1)
        if [ -n "$latest" ]; then
            echo "最新日志内容（最后20行）："
            echo "-----------------------------------"
            tail -20 "$latest"
            echo "-----------------------------------"
        fi
    else
        echo "日志目录为空"
    fi
    echo ""
}

# 清理日志
clean_logs() {
    echo -e "${YELLOW}清理日志文件...${NC}"
    rm -rf logs/*
    echo "✓ 已清理"
    echo ""
}

# 运行完整演示流程
run_demo() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  完整演示流程${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    echo -e "${GREEN}步骤1: 准备环境${NC}"
    prepare_env

    echo -e "${GREEN}步骤2: 启动基础监控${NC}"
    echo "请在另一个终端运行: sudo ./netfilter_trace.bt"
    echo "然后按回车继续..."
    read

    echo -e "${GREEN}步骤3: 生成流量${NC}"
    generate_traffic

    echo "等待观察输出... (5秒)"
    sleep 5

    echo -e "${GREEN}步骤4: 停止监控并查看日志${NC}"
    show_logs

    echo -e "${GREEN}步骤5: 启动包装脚本演示${NC}"
    echo "请运行: ./netfilter_wrapper.sh"
    echo "然后按回车继续..."
    read

    echo -e "${GREEN}步骤6: 生成持续流量${NC}"
    echo "在监控期间运行此命令生成流量..."
    generate_mixed_traffic

    echo -e "${GREEN}步骤7: 查看最终日志${NC}"
    show_logs

    echo -e "${GREEN}演示完成！${NC}"
    echo ""
    echo "下一步："
    echo "  1. 停止所有监控进程"
    echo "  2. 查看日志分析: python3 netfilter_analyzer.py --mode file --file logs/xxx.log"
    echo "  3. 清理: $0 clean"
    echo ""
}

# 主函数
main() {
    case "${1:-help}" in
        prepare)
            prepare_env
            ;;
        traffic)
            generate_traffic
            ;;
        mixed)
            generate_mixed_traffic
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_logs
            ;;
        demo)
            run_demo
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
