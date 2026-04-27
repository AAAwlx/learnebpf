#!/bin/bash
# 清理编译产物脚本

echo "=========================================="
echo "   Netfilter Trace - 清理编译产物"
echo "=========================================="
echo ""

# 计数器
cleaned_count=0

# 清理 BPF 对象文件
echo "1. 清理 BPF 对象文件..."
if rm -f netfilter_trace_bpfel.o netfilter_trace_bpfeb.o netfilter_trace_x86_bpfel.o 2>/dev/null; then
    echo "   ✓ 删除 .o 文件"
    cleaned_count=$((cleaned_count + 1))
else
    echo "   - 没有找到 .o 文件"
fi

# 清理生成的 Go 文件
echo "2. 清理生成的 BPF Go 文件..."
if rm -f netfilter_trace_bpfel.go netfilter_trace_bpfeb.go netfilter_trace_x86_bpfel.go 2>/dev/null; then
    echo "   ✓ 删除 _bpf*.go 文件"
    cleaned_count=$((cleaned_count + 1))
else
    echo "   - 没有找到 _bpf*.go 文件"
fi

# 清理可执行文件
echo "3. 清理可执行文件..."
if rm -f netfilter_trace 2>/dev/null; then
    echo "   ✓ 删除 netfilter_trace 可执行文件"
    cleaned_count=$((cleaned_count + 1))
else
    echo "   - 没有找到 netfilter_trace 可执行文件"
fi

# 清理 Go 依赖文件
echo "4. 清理 Go 依赖文件..."
if rm -f go.sum 2>/dev/null; then
    echo "   ✓ 删除 go.sum"
    cleaned_count=$((cleaned_count + 1))
else
    echo "   - 没有找到 go.sum"
fi

echo ""
echo "=========================================="
if [ $cleaned_count -gt 0 ]; then
    echo "✓ 清理完成！删除了 $cleaned_count 类文件"
    echo ""
    echo "保留的源文件："
    echo "  - netfilter_trace.bpf.c (BPF 源代码)"
    echo "  - main.go (Go 主程序)"
    echo "  - vmlinux.h (内核头文件)"
    echo "  - build_and_run.sh (构建脚本)"
    echo "  - clean.sh (清理脚本)"
    echo "  - 其他文档文件 (.md)"
else
    echo "没有找到需要清理的文件"
fi
echo "=========================================="
