# Netfilter Trace 工具集

完整的 Linux netfilter 钩子点监控工具套件，支持多种使用方式。

## 📁 项目结构

```text
毕设/
├── netfilter_trace.bt              # bpftrace 脚本（核心）
├── netfilter_wrapper.sh            # 🌟 交互式过滤工具（推荐）
├── netfilter_analyzer.py           # 🤖 AI 智能分析器
├── setup_env.sh                    # API Key 配置助手
│
├── logs/                           # 日志目录
│   └── netfilter_trace_*.log
│
├── README.md                       # 本文档
├── QUICKREF.md                     # 快速参考
├── WRAPPER_USAGE.md                # 过滤工具详细文档
├── AI_ANALYSIS.md                  # 🤖 AI分析功能文档
├── COMPARISON.md                   # 方案对比文档
```

## 🚀 快速开始

### 方式1：交互式过滤工具（推荐新手）⭐

```bash
./netfilter_wrapper.sh
```

**功能**：

- 按IP过滤、按Hook过滤、按结果过滤
- 自动日志记录
- 彩色菜单界面
- **🤖 AI 智能分析** - 实时生成网络分析报告

详见 [WRAPPER_USAGE.md](WRAPPER_USAGE.md) | [AI_ANALYSIS.md](AI_ANALYSIS.md)

---

### 方式2：直接使用 bpftrace

```bash
sudo ./netfilter_trace.bt
```

**特点**：无需编译，直接运行

---

### 方式3：编译型 eBPF 程序

```bash
cd modular
./build_and_run.sh
```

**特点**：高性能，适合生产环境

详见 [modular/README.md](modular/README.md)

---

## 📊 监控的 10 个 Netfilter 钩子

1. **ip_rcv** - IP 包接收入口
2. **ip_rcv_finish** - IP 包接收完成
3. **ip_local_deliver** - 本地投递
4. **ip_local_deliver_finish** - 本地投递完成
5. **ip_forward** - 转发判断
6. **ip_mr_forward** - 组播转发
7. **ip_local_out** - 本地输出
8. **ip_output** - IP 层输出
9. **ip_mc_output** - 组播输出
10. **ip_finish_output** - 最终输出

**plus**: **nf_hook_slow** - netfilter 核心判断函数（返回 ACCEPT/DROP）

## 📖 使用场景示例

### 场景0：制作演示视频 🎬

**想要录制演示视频？**

完整的演示视频制作指南已为你准备：

```bash
# 查看演示指南
cat DEMO_INDEX.md

# 准备演示环境
./demo_helper.sh prepare

# 自动化演示流程
./demo_helper.sh demo
```

**适合场景**：
- 项目答辩演示
- 技术分享会议
- 产品功能介绍
- 教学视频制作

---

### 场景1：AI 智能网络分析 🤖

```bash
# 配置 API Key（一次性）
./setup_env.sh

# 启动 AI 分析
./netfilter_wrapper.sh
→ 选择 8 (AI 分析模式)
→ 选择 2 (AI 深度分析)
→ 设置报告间隔 60 秒

# 自动生成包含以下内容的报告：
# - 流量模式分析
# - 安全风险评估
# - 性能瓶颈识别
# - 具体优化建议
```

### 场景2：调试网络连接问题

```bash
# 启动交互式工具
./netfilter_wrapper.sh

# 选择: 1 (按IP过滤) → 输入你的IP
#       3 (按结果过滤) → 2 (DROP)
#       7 (开始监控)

# 在另一个终端触发问题
curl https://example.com
```

### 场景2：监控本机所有网络活动

```bash
sudo ./netfilter_trace.bt
```

### 场景3：性能分析

```bash
cd modular
./build_and_run.sh

# 查看延迟
sudo cat /sys/kernel/debug/tracing/trace_pipe
```

### 场景4：安全审计

```bash
./netfilter_wrapper.sh

# 开启日志模式
# 监控所有 DROP 的包
```

## 🎯 输出格式

### IP 层函数输出

```
[ip_rcv] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789
 ↑        ↑               ↑            ↑
函数名    源IP          目的IP       skb地址
```

### Netfilter 判定输出

```
[ACCEPT] 192.168.1.100 -> 8.8.8.8 | skb=0xffff888123456789
 ↑        ↑               ↑            ↑
结果     源IP          目的IP       skb地址

[nf_hook_slow] 192.168.1.100 -> 8.8.8.8 | skb:0xffff... | hook_num:0
 ↑              ↑               ↑              ↑
函数名        源IP          目的IP        Hook编号
```

## 🔍 Hook 编号说明

```
0 - NF_INET_PRE_ROUTING  (刚进入，路由决策前)
1 - NF_INET_LOCAL_IN     ( destined for 本机)
2 - NF_INET_FORWARD      (需要转发)
3 - NF_INET_LOCAL_OUT    (本机发出)
4 - NF_INET_POST_ROUTING (路由后，即将发出)
```

## 📚 文档索引

| 文档 | 内容 |
|------|------|
| [QUICKREF.md](QUICKREF.md) | 快速参考卡片 |
| [AI_ANALYSIS.md](AI_ANALYSIS.md) | 🤖 AI 分析功能完整指南 |
| [WRAPPER_USAGE.md](WRAPPER_USAGE.md) | 过滤工具详细使用指南 |
| [COMPARISON.md](COMPARISON.md) | 三种实现方案对比 |
| [modular/README.md](modular/README.md) | eBPF C 版本架构说明 |

## 🛠️ 系统要求

### 基础功能

```bash
# 检查是否安装 bpftrace
bpftrace -V

# 安装
sudo apt install bpftrace
```

### AI 分析功能（可选）
```bash
# 检查 Python
python3 --version

# 安装 anthropic 库（AI 深度分析需要）
pip3 install anthropic

# 或使用配置助手
./setup_env.sh
```

### eBPF C 版本
```bash
# 需要
- Clang/LLVM
- Go 1.18+
- Linux 内核 5.0+
- libbpf
```

## 🔧 故障排查

### 没有 IP 地址显示？

**原因**：某些 hook 点 skb->data 不指向 IP 头

**解决**：优先观察 `ip_rcv` 和 `nf_hook_slow` 的输出

### 没有 root 权限？

```bash
# 配置 sudoers
sudo visudo
# 添加: username ALL=(ALL) NOPASSWD: /usr/bin/bpftrace
```

### 日志文件在哪里？

```
./logs/netfilter_trace_YYYYMMDD_HHMMSS.log
```

## 📈 性能对比

| 方案 | CPU占用 | 内存占用 | 启动时间 | 适用场景 |
|------|---------|----------|----------|----------|
| bpftrace | 0.1-0.5% | ~5MB | <0.5s | 调试、学习 |
| eBPF C | <0.1% | ~1MB | 1-2s | 生产环境 |

## 🤝 贡献

欢迎改进：
- 添加更多过滤条件
- 优化性能
- 补充文档
- 修复 bug

## 📄 许可

Dual BSD/GPL（与 eBPF 程序一致）

## 🎓 学习资源

- [eBPF 官方文档](https://ebpf.io/)
- [bpftrace 参考指南](https://github.com/iovisor/bpftrace)
- [Netfilter 原理](https://www.kernel.org/doc/Documentation/networking/nf_hook_operations.txt)

---

**推荐使用方式**：
- 🔰 **学习/调试**：`./netfilter_wrapper.sh`
- 🏭 **生产环境**：`cd modular && ./build_and_run.sh`
- ⚡ **快速验证**：`sudo ./netfilter_trace.bt`
