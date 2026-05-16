# AI 智能分析功能使用指南

## 功能概述

netfilter_wrapper 现在集成了 AI 智能分析功能，可以实时监控网络流量并生成智能报告。

### 两种分析模式

#### 1. 本地分析模式 ⚡
- **速度**：快速，实时
- **依赖**：仅需要 Python 3
- **功能**：统计分析、模式识别、安全评估

#### 2. AI 深度分析模式 🤖
- **速度**：较慢（需要 API 调用）
- **依赖**：Anthropic API Key
- **功能**：深度分析、智能建议、异常检测

---

## 快速开始

### 启动 AI 分析模式

```bash
cd 毕设
./netfilter_wrapper.sh
```

在菜单中选择：
```
8. AI 智能分析模式
```

### 分析流程

1. **选择分析模式**
   - 选项1：本地分析（推荐首次使用）
   - 选项2：AI 深度分析（需要 API Key）

2. **配置报告间隔**
   - 默认30秒生成一次报告
   - 可根据需要调整

3. **自动监控与分析**
   - 实时收集网络数据
   - 定期生成分析报告
   - Ctrl+C 退出并查看最终报告

---

## 使用场景

### 场景1：网络安全审计

**需求**：检查是否有异常连接或攻击

**操作步骤**：
```bash
./netfilter_wrapper.sh
→ 选择 8 (AI分析)
→ 选择 1 (本地分析)
→ 设置间隔 15 秒
```

**预期报告**：
```
🔒 安全分析
  ⚠️  警告: 丢包率较高 (25.3%)
  ℹ️  检测到 5 个公网IP访问
  ℹ️  检测到 3 个内网IP访问
```

---

### 场景2：性能优化

**需求**：分析网络性能瓶颈

**操作步骤**：
```bash
./netfilter_wrapper.sh
→ 选择 2 (按Hook过滤) → 输入 0 (PRE_ROUTING)
→ 选择 8 (AI分析)
→ 选择 2 (AI深度分析)
→ 输入 API Key
```

**预期报告**：
```
⚡ SKB 生命周期分析
  平均处理步数: 4.2 次
  最多步数: 8 次

💡 优化建议
  - 考虑优化 netfilter 规则顺序
  - 减少不必要的钩子点
```

---

### 场景3：故障排查

**需求**：排查为什么某个应用无法连接

**操作步骤**：
```bash
./netfilter_wrapper.sh
→ 选择 1 (按IP过滤) → 输入应用服务器IP
→ 选择 3 (按结果过滤) → 2 (DROP)
→ 选择 8 (AI分析)
```

**预期报告**：
```
🔒 安全分析
  ⚠️  警告: 丢包率较高 (100.0%)
  所有到目标IP的包都被丢弃

💡 优化建议
  ⚠️  丢包率过高，建议检查:
     - 防火墙规则是否过于严格
     - 是否有IP封禁
     - 网络连接是否正常
```

---

## 本地分析报告内容

### 1. 总体统计
```
📈 总体统计
  接受 (ACCEPT): 1523 (98.2%)
  丢弃 (DROP):   28 (1.8%)
  唯一源IP: 45 个
  唯一目标IP: 12 个
```

### 2. Hook 点分布
```
🎣 Hook 点分布
  NF_INET_PRE_ROUTING: 456 次 (29.4%)
  NF_INET_LOCAL_IN:    389 次 (25.1%)
  NF_INET_LOCAL_OUT:   312 次 (20.1%)
```

### 3. 函数调用频率
```
⚙️  函数调用TOP5
  nf_hook_slow:       1452 次 (93.6%)
  ip_rcv:             1203 次 (77.5%)
  ip_local_deliver:    987 次 (63.6%)
```

### 4. 热门IP流
```
🌐 热门IP流 TOP5
  192.168.1.100 -> 8.8.8.8:     234 次 (15.1%)
  192.168.1.100 -> 1.1.1.1:     189 次 (12.2%)
  192.168.1.100 -> 10.0.0.1:    145 次 (9.4%)
```

### 5. 安全分析
```
🔒 安全分析
  ✓ 丢包率正常 (1.8%)
  ℹ️  检测到 8 个公网IP访问
  ℹ️  检测到 37 个内网IP访问
```

### 6. 性能分析
```
⚡ SKB 生命周期分析
  平均处理步数: 3.8 次
  最多步数: 7 次
```

### 7. 优化建议
```
💡 优化建议
  ℹ️  连接数较多，建议:
     - 检查是否有异常连接
     - 考虑增加连接跟踪限制
```

---

## AI 深度分析报告

### 额外功能

使用 Anthropic Claude API 进行深度分析：

1. **流量模式识别**
   - 检测异常流量模式
   - 识别周期性行为
   - 发现潜在攻击

2. **智能建议**
   - 基于最佳实践的优化建议
   - 具体的配置改进方案
   - 风险评估和缓解措施

3. **趋势分析**
   - 长期趋势识别
   - 预测潜在问题
   - 容量规划建议

---

## 配置 Anthropic API

### 方法1：环境变量（推荐）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export ANTHROPIC_API_KEY="your-api-key-here"

# 重新加载配置
source ~/.bashrc
```

### 方法2：临时设置

```bash
# 当前会话
export ANTHROPIC_API_KEY="your-api-key-here"

# 运行分析
./netfilter_wrapper.sh
```

### 方法3：运行时输入

启动时手动输入 API Key（不会保存）

### 获取 API Key

1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账号
3. 创建 API Key
4. 充值余额（按使用量计费）

---

## 命令行直接使用分析器

除了通过包装脚本，也可以直接使用 Python 分析器：

### 实时分析（流模式）

```bash
# 本地分析
sudo bpftrace netfilter_trace.bt 2>/dev/null | \
  python3 netfilter_analyzer.py --mode stream --interval 30

# AI 分析
sudo bpftrace netfilter_trace.bt 2>/dev/null | \
  python3 netfilter_analyzer.py --mode stream --interval 30 \
  --api-key "$ANTHROPIC_API_KEY"
```

### 日志文件分析

```bash
# 分析已有日志
python3 netfilter_analyzer.py --mode file --file logs/netfilter_trace_20240427_123456.log

# 使用 AI 分析
python3 netfilter_analyzer.py --mode file --file logs/netfilter_trace_20240427_123456.log \
  --api-key "$ANTHROPIC_API_KEY"
```

### 参数说明

```
--mode       运行模式: stream(实时) 或 file(文件)
--file       日志文件路径（file模式必需）
--api-key    Anthropic API Key（可选）
--interval   实时模式下报告间隔（秒，默认30）
--min-records 最小记录数才生成报告（默认10）
```

---

## 分析输出示例

### 本地分析示例

```bash
$ python3 netfilter_analyzer.py --mode file --file logs/test.log

🚀 网络流量分析器已启动
📅 启动时间: 2024-04-27 20:45:30
📊 最小记录数: 10
⏱️  报告间隔: 30 秒
------------------------------------------------------------

============================================================
📊 网络流量分析报告
============================================================
⏰ 分析时间: 2024-04-27 20:45:31
📦 记录总数: 1234 条

📈 总体统计
  接受 (ACCEPT): 1198 (97.1%)
  丢弃 (DROP):    36 (2.9%)
  唯一源IP: 67 个
  唯一目标IP: 23 个

🎣 Hook 点分布
  NF_INET_PRE_ROUTING: 456 次 (29.4%)
  NF_INET_LOCAL_IN:    389 次 (25.1%)
  ...

💡 优化建议
  ✓ 丢包率正常
  ℹ️  连接数较多，建议检查是否有异常连接
============================================================
```

### AI 分析示例

```bash
$ python3 netfilter_analyzer.py --mode file --file logs/test.log --api-key "sk-..."

============================================================
📊 网络流量分析报告
============================================================
...
[本地分析部分]

============================================================
🤖 AI 深度分析
============================================================

基于监控数据分析，我发现以下情况：

## 流量模式分析
1. 正常网络通信模式
2. 检测到周期性DNS查询流量
3. 未发现异常流量模式

## 安全风险评估
- 丢包率2.9%，属于正常范围
- 未发现明显的DDoS攻击迹象
- 建议监控192.168.1.100的异常连接行为

## 性能优化建议
1. 可以考虑优化 nf_hook_slow 的调用频率
2. 建议将常用规则放在前面
3. 可以使用连接跟踪提高性能

...更多详细建议...
```

---

## 高级用法

### 1. 定期分析并保存报告

```bash
#!/bin/bash
# daily_analysis.sh

LOG_FILE="logs/netfilter_trace_$(date +%Y%m%d).log"
REPORT_FILE="reports/analysis_$(date +%Y%m%d).txt"

# 运行监控1小时
timeout 3600 sudo bpftrace netfilter_trace.bt 2>/dev/null | tee "$LOG_FILE" | \
  python3 netfilter_analyzer.py --mode stream --interval 300 --api-key "$ANTHROPIC_API_KEY" \
  > "$REPORT_FILE"

echo "报告已生成: $REPORT_FILE"
```

### 2. 结合过滤条件分析

```bash
# 只分析 DROP 的包
sudo bpftrace netfilter_trace.bt 2>/dev/null | \
  grep '\[DROP\]' | \
  python3 netfilter_analyzer.py --mode stream --interval 60
```

### 3. 后台运行分析

```bash
nohup sudo bpftrace netfilter_trace.bt 2>/dev/null | \
  python3 netfilter_analyzer.py --mode stream --interval 300 \
  > analysis_report.txt 2>&1 &
```

---

## 故障排查

### 问题1：Python 模块缺失

```bash
# 错误: ModuleNotFoundError: No module named 'anthropic'

# 解决：安装 anthropic 库（仅 AI 模式需要）
pip3 install anthropic

# 或使用本地分析模式（无需安装）
python3 netfilter_analyzer.py --mode file --file logs/test.log
```

### 问题2：API 调用失败

```bash
# 错误: AI分析失败: Invalid API Key

# 检查 API Key
echo $ANTHROPIC_API_KEY

# 确认格式（应该以 sk-ant- 开头）
```

### 问题3：没有足够的记录

```bash
# ⚠️ 记录数不足 (5 < 10)，无法生成报告

# 解决：降低最小记录数
python3 netfilter_analyzer.py --mode stream --min-records 5

# 或等待更长时间
```

---

## 性能考虑

### 资源占用

- **CPU**: 本地分析 < 1%，AI 分析 < 2%
- **内存**: ~50MB（Python + 分析数据）
- **网络**: AI 分析每次约 1-5KB 数据传输

### 建议配置

- **报告间隔**：生产环境建议 60-300 秒
- **最小记录数**：建议 10-50 条
- **API 频率**：避免过于频繁调用（最小间隔30秒）

---

## 总结

AI 智能分析功能提供了：

✅ **实时分析** - 持续监控并生成报告
✅ **多种模式** - 本地快速分析 + AI 深度分析
✅ **灵活配置** - 可调整报告间隔和过滤条件
✅ **智能建议** - 基于数据给出优化建议
✅ **易于使用** - 交互式菜单，无需复杂命令

推荐使用方式：
- 🔰 **学习/测试**：本地分析模式
- 🏢 **生产环境**：AI 深度分析（获得更专业的建议）
- ⚡ **快速验证**：降低报告间隔到 10-15 秒
