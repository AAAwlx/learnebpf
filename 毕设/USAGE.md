# 🎯 Netfilter Trace Monitor - 快速使用指南

基于 **libbpf-go** 的网络协议栈函数监控工具。

## 📦 已创建的文件

```
netfilter_trace.bpf.c     - BPF 内核程序
main.go                    - Go 用户程序
vmlinux.h                  - 内核类型定义
go.mod                     - Go 模块文件
Makefile                   - 构建脚本
build_and_run.sh          - 一键构建运行脚本
README_LIBBPFGO.md         - 详细文档
```

## 🚀 快速开始

### 方法 1：使用自动化脚本（推荐）

```bash
cd /home/ylx/我的项目/learnebpf/netfilter
./build_and_run.sh
```

### 方法 2：手动构建

```bash
# 1. 生成 BPF Go 文件
GOPACKAGE=main bpf2go -cc clang -cflags '-O2 -g -Wall' \
  -target bpfel,amd64,bpfeb netfilter_trace netfilter_trace.bpf.c \
  -- -I/usr/include/bpf

# 2. 安装依赖
go mod init netfilter-trace
go get github.com/cilium/ebpf@latest
go mod tidy

# 3. 编译
go build -o netfilter_trace main.go netfilter_trace_bpfel.go

# 4. 运行
sudo ./netfilter_trace
```

## 📊 查看输出

### 在另一个终端运行：

```bash
# 查看完整的内核追踪输出
sudo cat /sys/kernel/debug/tracing/trace_pipe

# 或只查看我们的输出
sudo cat /sys/kernel/debug/tracing/trace_pipe | grep "Function:"
```

## 🎯 触发测试流量

```bash
# Ping 测试
ping 8.8.8.8

# HTTP 请求
curl https://www.google.com

# DNS 查询
nslookup google.com
```

## 📋 输出格式

```
Function: ip_rcv | skb: 0xffff888123456789 | args: [0xffff888123456789, 0x0, 0x0, 0x0]
Function: ip_rcv_finish | skb: 0xffff888123456789 | args: [0xffff888123456789, 0x0, 0x0, 0x0]
Function: ip_local_deliver | skb: 0xffff888123456789 | args: [0xffff888123456789, 0x0, 0x0, 0x0]
```

**字段说明：**
- `Function` - 函数名
- `skb` - 第一个参数（通常是 struct sk_buff* 地址）
- `args` - 所有4个参数的值（十六进制）

## 🔍 监控的函数

1. `ip_rcv` - 接收 IPv4 数据包
2. `ip_rcv_finish` - 完成接收
3. `ip_local_deliver` - 本地交付
4. `ip_local_deliver_finish` - 完成本地交付
5. `ip_forward` - 转发数据包
6. `ip_mr_forward` - 多播转发
7. `ip_local_out` - 本地发送
8. `ip_output` - 输出
9. `ip_mc_output` - 多播输出
10. `ip_finish_output` - 完成输出

## 🛠️ 故障排除

### 问题 1：编译失败 - 缺少依赖
```bash
# 安装 Go 和 eBPF 工具
sudo pacman -S go clang llvm bpftool libbpf
```

### 问题 2：无法附加 kprobe
```bash
# 检查函数符号是否存在
grep 'ip_rcv' /proc/kallsyms

# 查看内核日志
sudo dmesg | tail
```

### 问题 3：权限被拒绝
```bash
# 确保使用 sudo
sudo ./netfilter_trace

# 或者配置 capabilities
sudo setcap cap_perfmod,cap_net_raw,cap_sys_admin+ep ./netfilter_trace
```

### 问题 4：网络超时
```bash
# 使用国内 Go 代理
export GOPROXY=https://goproxy.cn,direct
go mod download
```

## 💡 工作原理

```
用户触发网络流量 (ping/curl)
    ↓
内核调用网络函数
    ↓
kprobe 捕获函数调用
    ↓
读取寄存器参数
    ↓
bpf_printk 内核打印
    ↓
输出到 trace_pipe
    ↓
用户查看输出
```

## 🎓 关键技术点

1. **libbpf-go**: 使用 Go 语言的 eBPF 库
2. **bpf2go**: 将 BPF C 代码转换为 Go 代码
3. **kprobe**: 内核动态探针技术
4. **pt_regs**: 读取函数参数（寄存器）
5. **bpf_printk**: 内核日志输出

## 📝 代码特点

- ✅ **简洁**: 直接在内核打印，无需复杂的用户空间处理
- ✅ **高效**: 使用 kprobe，性能开销小
- ✅ **完整**: 监控所有关键网络函数
- ✅ **实时**: 函数调用即时输出

## 🔗 相关资源

- [libbpf-go GitHub](https://github.com/cilium/ebpf)
- [bpf2go 文档](https://github.com/cilium/ebpf/tree/main/cmd/bpf2go)
- [eBPF 官方文档](https://ebpf.io/)

## 🎉 成功标志

如果看到以下输出，说明程序运行成功：

```
✓ Attached kprobe: ip_rcv
✓ Attached kprobe: ip_rcv_finish
✓ Attached kprobe: ip_local_deliver
...
========================================
Netfilter Trace Monitor Started!
Attached 10 kprobes successfully
========================================
```

祝使用愉快！🚀
