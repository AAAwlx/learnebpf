# Netfilter Trace Monitor - 基于 libbpf-go

使用 libbpf-go 框架监控 Linux 内核网络协议栈函数调用。

## 📋 监控的函数

- `ip_rcv` - 接收 IPv4 数据包
- `ip_rcv_finish` - 完成接收处理
- `ip_local_deliver` - 本地交付
- `ip_local_deliver_finish` - 完成本地交付
- `ip_forward` - 转发数据包
- `ip_mr_forward` - 多播转发
- `ip_local_out` - 本地发送
- `ip_output` - 输出
- `ip_mc_output` - 多播输出
- `ip_finish_output` - 完成输出

## 🔧 环境要求

- Linux 内核 5.8+ (支持 BPF CO-RE)
- Go 1.21+
- clang/llvm
- bpftool

### Arch Linux 安装
```bash
sudo pacman -S go clang llvm bpftool libbpf
```

## 🚀 快速开始

### 1. 安装 bpf2go 工具
```bash
go install github.com/cilium/ebpf/cmd/bpf2go@latest
```

### 2. 构建程序
```bash
cd /home/ylx/我的项目/learnebpf/netfilter
make all
```

### 3. 运行监控
```bash
sudo ./netfilter_trace
```

### 4. 查看内核输出（在另一个终端）
```bash
# 查看完整输出
sudo cat /sys/kernel/debug/tracing/trace_pipe

# 或过滤我们的输出
sudo cat /sys/kernel/debug/tracing/trace_pipe | grep "Function:"
```

## 📊 输出格式

```
<...>-1234 [001] .... 12345.678901: bpf_trace_printk: Function: ip_rcv | skb: 0xffff888123456789 | args: [0xffff888123456789, 0x0, 0x0, 0x0]
<...>-1234 [001] .... 12345.678905: bpf_trace_printk: Function: ip_rcv_finish | skb: 0xffff888123456789 | args: [0xffff888123456789, 0x0, 0x0, 0x0]
```

**字段说明：**
- `Function` - 函数名
- `skb` - Socket buffer 地址
- `args` - 4个参数的值（十六进制）

## 🎯 触发测试流量

在另一个终端运行以下命令来产生网络流量：

```bash
# Ping 测试
ping 8.8.8.8

# HTTP 请求
curl https://www.google.com

# 本地连接
nc -l 8080
```

## 🛠️ 开发和调试

### 重新生成 BPF 文件
```bash
make generate_bpf
```

### 只编译 Go 程序
```bash
make build_go
```

### 清理构建文件
```bash
make clean
```

### 查看帮助
```bash
make help
```

## 📝 代码结构

```
netfilter_trace.bpf.c  - BPF 程序（内核态）
main.go                 - Go 程序（用户态）
vmlinux.h               - 内核类型定义
Makefile                - 构建脚本
go.mod                  - Go 依赖管理
```

## 🔍 工作原理

1. **BPF 程序编译**
   ```
   netfilter_trace.bpf.c → bpf2go → netfilter_trace_bpfel.go + netfilter_trace_bpfel.o
   ```

2. **程序运行**
   ```
   main.go 加载 BPF 程序 → 附加到 kprobe → 监控函数调用
   ```

3. **数据输出**
   ```
   内核函数调用 → bpf_printk → trace_pipe → 用户查看
   ```

## ⚠️ 故障排除

### 问题 1：无法加载 BPF 程序
```bash
# 检查内核 BTF 支持
ls /sys/kernel/btf/vmlinux

# 检查权限
sudo -v
```

### 问题 2：kprobe 附加失败
```bash
# 检查符号是否存在
grep 'ip_rcv' /proc/kallsyms

# 查看程序错误输出
sudo dmesg | tail
```

### 问题 3：没有输出
```bash
# 1. 确认程序在运行
ps aux | grep netfilter_trace

# 2. 触发网络流量
ping 8.8.8.8

# 3. 检查 trace_pipe
sudo cat /sys/kernel/debug/tracing/trace_pipe
```

## 🎓 学习要点

### 1. libbpf-go 框架
- 使用 `bpf2go` 工具生成 Go 绑定代码
- 通过 `loadBpfObjects()` 加载 BPF 程序
- 使用 `link.Kprobe()` 附加到内核函数

### 2. kprobe 工作原理
- 在内核函数入口处插入探针
- 可以读取函数参数（通过 `PT_REGS_PARM*`）
- 使用 `bpf_printk` 输出调试信息

### 3. 参数读取
```c
__u64 param1 = PT_REGS_PARM1(ctx);  // 第一个参数
__u64 param2 = PT_REGS_PARM2(ctx);  // 第二个参数
// ...
```

对于网络函数，第一个参数通常是 `struct sk_buff *`（skb 地址）。

## 📚 相关资源

- [Cilium eBPF Go Library](https://github.com/cilium/ebpf)
- [bpf2go Documentation](https://github.com/cilium/ebpf/blob/main/cmd/bpf2go/README.md)
- [Linux Kernel BPF Documentation](https://www.kernel.org/doc/html/latest/bpf/)

## 🎉 特点

- ✅ **轻量级** - 直接内核打印，无用户空间处理开销
- ✅ **实时性** - 函数调用即时打印
- ✅ **完整性** - 监控所有关键网络函数
- ✅ **现代化** - 使用 libbpf-go 和 CO-RE 技术

祝学习愉快！🚀
