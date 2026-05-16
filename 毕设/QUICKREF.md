# 快速参考 - netfilter_trace 工具集

## 🚀 快速开始

```bash
cd 毕设
./netfilter_wrapper.sh
```

## 📋 功能清单

### 1️⃣ 实时监控
- 选择菜单选项 `7`
- 无过滤，实时显示所有网络活动

### 2️⃣ 按IP过滤
- 选择 `1` → 输入IP地址 → 选择 `7`
- 只显示特定IP的流量

### 3️⃣ 按Hook过滤
- 选择 `2` → 输入编号(0-4) → 选择 `7`
- 监控特定netfilter钩子点

### 4️⃣ 按结果过滤
- 选择 `3` → 选择类型(ACCEPT/DROP/OTHER) → 选择 `7`
- 只看接受/丢弃的包

### 5️⃣ 日志模式
- 选择 `5` 开启日志模式 → 选择 `7`
- 自动保存到 `./logs/`

### 6️⃣ AI智能分析 ⭐
- 选择 `8` → 选择分析模式
- 实时生成网络分析报告

---

## 🎯 常用场景

### 调试连接问题
```bash
./netfilter_wrapper.sh
→ 1 (IP过滤) → 输入你的IP
→ 3 (结果过滤) → 2 (DROP)
→ 7 (开始监控)
```

### 安全审计
```bash
./netfilter_wrapper.sh
→ 5 (开启日志模式)
→ 7 (开始监控)

# 另一个终端分析
python3 netfilter_analyzer.py --mode file --file logs/latest.log
```

### 性能优化
```bash
./netfilter_wrapper.sh
→ 8 (AI分析)
→ 2 (AI深度分析)
→ 输入报告间隔: 60
```

### 追踪特定包
```bash
# 先找到skb地址
sudo ./netfilter_trace.bt | grep "目标IP"

# 再追踪该skb
./netfilter_wrapper.sh
→ 4 (SKB过滤) → 输入skb地址
→ 7 (开始监控)
```

---

## 🤖 AI分析快速参考

### 启动AI分析
```bash
./netfilter_wrapper.sh
→ 选择 8
→ 选择 1 (本地) 或 2 (AI)
```

### 配置API Key
```bash
./setup_env.sh
```

### 命令行直接使用
```bash
# 实时分析
sudo bpftrace netfilter_trace.bt | \
  python3 netfilter_analyzer.py --mode stream

# 文件分析
python3 netfilter_analyzer.py --mode file --file logs/xxx.log
```

---

## 📊 输出格式说明

### 基本输出
```
[ip_rcv] 源IP -> 目的IP | skb:0x地址
```

### Netfilter判定
```
[ACCEPT] 源IP -> 目的IP | skb=0x地址
[DROP]   源IP -> 目的IP | skb=0x地址

[nf_hook_slow] 源 -> 目的 | skb:0x... | hook_num:0
```

### AI分析报告
```
📊 网络流量分析报告
============================================================
📈 总体统计
🎣 Hook 点分布
⚙️  函数调用TOP5
🌐 热门IP流 TOP5
🔒 安全分析
⚡ SKB 生命周期分析
💡 优化建议
============================================================
```

---

## ⌨️ 快捷命令

### 查看实时日志
```bash
sudo cat /sys/kernel/debug/tracing/trace_pipe | grep '\['
```

### 查看历史日志
```bash
ls -lh logs/
cat logs/netfilter_trace_*.log | grep "192.168.1.1"
```

### 后台运行
```bash
nohup ./netfilter_wrapper.sh > /dev/null 2>&1 &
```

### 统计DROP包
```bash
cat logs/*.log | grep "\[DROP\]" | wc -l
```

---

## 🔧 系统要求

### 必需
- Linux 内核 4.18+
- sudo 权限
- bpftrace

### AI分析可选
- Python 3.7+
- anthropic 库（`pip3 install anthropic`）
- Anthropic API Key

---

## 📚 文档索引

| 文档 | 内容 |
|------|------|
| [README.md](README.md) | 项目总览和快速开始 |
| [WRAPPER_USAGE.md](WRAPPER_USAGE.md) | 过滤工具详细使用指南 |
| [AI_ANALYSIS.md](AI_ANALYSIS.md) | AI分析功能完整文档 |
| [COMPARISON.md](COMPARISON.md) | 三种实现方案对比 |
| [modular/README.md](modular/README.md) | eBPF C版本说明 |

---

## 🆘 故障排查

### 没有输出
- 检查是否有流量：`ping 8.8.8.8`
- 检查sudo权限
- 确认bpftrace已安装

### IP显示0.0.0.0
- 正常现象（部分hook点）
- 优先观察 `ip_rcv` 和 `nf_hook_slow`

### 权限错误
```bash
sudo -v  # 测试sudo
sudo visudo  # 配置免密
```

### Python模块缺失
```bash
pip3 install anthropic  # AI模式需要
# 或使用本地分析模式（无需安装）
```

---

## 💡 最佳实践

1. **学习阶段**：使用本地分析模式，熟悉输出格式
2. **调试阶段**：开启日志模式，事后分析
3. **生产环境**：使用AI深度分析，获取专业建议
4. **长期监控**：设置合理报告间隔（60-300秒）
5. **安全审计**：定期分析DROP包，检查异常

---

## 📞 获取帮助

```bash
# 查看菜单
./netfilter_wrapper.sh

# 查看分析器帮助
python3 netfilter_analyzer.py --help

# 查看文档
cat README.md
cat AI_ANALYSIS.md
```

---

**推荐工作流**：
1. 先用 `./netfilter_wrapper.sh` 实时监控
2. 发现问题后开启日志模式记录
3. 使用 AI 分析模式生成报告
4. 根据建议优化配置
