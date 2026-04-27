#!/bin/bash
# Netfilter Trace Monitor - 构建和运行脚本

set -e

echo "=========================================="
echo "Netfilter Trace Monitor - Build & Run"
echo "=========================================="
echo ""

# 检查依赖
echo "1. 检查依赖..."
if ! command -v go &> /dev/null; then
    echo "错误: Go 未安装"
    exit 1
fi

if ! command -v clang &> /dev/null; then
    echo "错误: clang 未安装"
    exit 1
fi

if ! command -v bpf2go &> /dev/null; then
    echo "安装 bpf2go..."
    go install github.com/cilium/ebpf/cmd/bpf2go@latest
fi

echo "✓ 所有依赖已就绪"
echo ""

# 生成 BPF Go 文件
echo "2. 生成 BPF Go 文件..."
GOPACKAGE=main bpf2go -cc clang -cflags '-O2 -g -Wall' -target bpfel,amd64 netfilter_trace netfilter_trace.bpf.c -- -I/usr/include/bpf
echo "✓ BPF 文件生成完成"
echo ""

# 整理 Go 依赖
echo "3. 下载 Go 依赖..."
go mod init netfilter-trace 2>/dev/null || true
go get github.com/cilium/ebpf@latest
go mod tidy
echo "✓ Go 依赖准备完成"
echo ""

# 编译 Go 程序
echo "4. 编译程序..."
go build -o netfilter_trace main.go netfilter_trace_bpfel.go
echo "✓ 程序编译完成"
echo ""

# 运行程序
echo "5. 启动监控..."
echo "=========================================="
echo ""

sudo ./netfilter_trace
