# netfilter_wrapper.sh 使用指南

## 功能特性

交互式包装脚本，为 bpftrace netfilter_trace 提供灵活的过滤功能：

- ✅ **按 IP 地址过滤** - 只显示特定 IP 的流量
- ✅ **按 Hook 编号过滤** - 监控特定 netfilter 钩子点
- ✅ **按处理结果过滤** - 只看 ACCEPT/DROP/OTHER
- ✅ **按 SKB 地址过滤** - 追踪特定数据包
- ✅ **日志模式** - 全量或过滤后写入日志文件
- ✅ **彩色界面** - 清晰的状态显示
- ✅ **组合过滤** - 支持多个条件同时生效

## 快速开始

### 启动交互式界面

```bash
cd /home/ylx/我的项目/learnebpf/毕设
./netfilter_wrapper.sh
```

## 使用场景示例

### 场景1：监控特定 IP 的所有流量

**需求**：只关心 IP 192.168.1.100 的网络活动

**操作步骤**：
1. 运行 `./netfilter_wrapper.sh`
2. 选择 `1` (按 IP 过滤)
3. 输入 `192.168.1.100`
4. 选择 `7` (开始监控)

**输出示例**：
```
[ACCEPT] 192.168.1.100 -> 8.8.8.8 | skb=0xffff888123456789
[nf_hook_slow] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789 | hook_num:0
```

---

### 场景2：只监控被丢弃的数据包

**需求**：排查为什么某些连接失败

**操作步骤**：
1. 选择 `3` (按结果过滤)
2. 选择 `2` (DROP)
3. 选择 `7` (开始监控)

**输出示例**：
```
[DROP] 10.0.0.5 -> 10.0.0.8 | skb=0xffff888456789abc
```

---

### 场景3：监控 PREROUTING 钩子

**需求**：查看所有进入系统的包

**操作步骤**：
1. 选择 `2` (按 Hook 过滤)
2. 输入 `0` (NF_INET_PRE_ROUTING)
3. 选择 `5` (开启日志模式)
4. 选择 `7` (开始监控)

**输出示例**：
```
[nf_hook_slow] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789 | hook_num:0
```

---

### 场景4：组合过滤 - 特定 IP 的 DROP 包

**需求**：查看 192.168.1.100 发起的连接中哪些被丢弃了

**操作步骤**：
1. 选择 `1` (按 IP 过滤) → 输入 `192.168.1.100`
2. 选择 `3` (按结果过滤) → 选择 `2` (DROP)
3. 选择 `5` (开启日志模式)
4. 选择 `7` (开始监控)

**输出示例**：
```
[DROP] 192.168.1.100 -> 192.168.1.200 | skb=0xffff888789abcdef
```

---

### 场景5：追踪特定数据包的生命周期

**需求**：查看一个 skb 在整个 netfilter 栈中的处理过程

**操作步骤**：
1. 先运行不带过滤的版本，找到感兴趣的 skb 地址
2. 按 Ctrl+C 停止
3. 选择 `4` (按 SKB 过滤) → 输入 `ffff888123456789`
4. 选择 `7` (开始监控)

**输出示例**：
```
[ip_rcv] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789
[ip_rcv_finish] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789
[nf_hook_slow] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789 | hook_num:0
[ACCEPT] 192.168.1.100 -> 8.8.8.8 | skb=0xffff888123456789
```

---

## Hook 编号对照表

```
0 - NF_INET_PRE_ROUTING  (刚进入网络栈，路由前)
1 - NF_INET_LOCAL_IN     ( destined for 本机)
2 - NF_INET_FORWARD      (需要转发)
3 - NF_INET_LOCAL_OUT    (本机发出)
4 - NF_INET_POST_ROUTING (路由后，即将发出)
```

## 日志管理

### 日志文件位置

```
./logs/netfilter_trace_YYYYMMDD_HHMMSS.log
```

### 开启日志模式的好处

1. **持久化记录** - 便于事后分析
2. **全量保存** - 日志包含完整输出，屏幕显示可过滤
3. **时间戳** - 文件名包含创建时间
4. **多会话** - 每次运行创建新日志文件

### 查看历史日志

```bash
# 列出所有日志文件
ls -lh ./logs/

# 查看最新日志
cat ./logs/netfilter_trace_*.log | tail -100

# 搜索特定 IP
cat ./logs/netfilter_trace_*.log | grep "192.168.1.100"

# 统计 DROP 包数量
cat ./logs/netfilter_trace_*.log | grep "\[DROP\]" | wc -l
```

### 清理日志

```bash
# 删除所有日志
rm -rf ./logs/

# 删除7天前的日志
find ./logs/ -name "*.log" -mtime +7 -delete
```

## 过滤逻辑说明

### 优先级

所有过滤条件是 **AND** 关系（同时满足）：

```
最终输出 = (IP匹配) AND (Hook匹配) AND (结果匹配) AND (SKB匹配)
```

### 示例

设置：
- IP: `192.168.1.100`
- Hook: `0`
- Result: `ACCEPT`

显示：来自 192.168.1.100 **且** 经过 PRE_ROUTING **且** 被接受的包

### 无过滤条件时

如果 1-4 都未设置，显示所有输出（全量模式）

## 故障排查

### 问题1：没有输出

**检查**：
1. 是否有网络流量？`ping 8.8.8.8`
2. 过滤条件是否太严格？尝试清除所有过滤
3. bpftrace 是否正确运行？查看错误信息

### 问题2：权限错误

```bash
# 确保可以运行 sudo
sudo -v

# 如果失败，配置 sudoers
sudo visudo
# 添加: username ALL=(ALL) NOPASSWD: /usr/bin/bpftrace
```

### 问题3：日志文件未创建

**检查**：
```bash
# 是否有 logs 目录
ls -ld ./logs/

# 手动创建
mkdir -p ./logs/
```

## 高级技巧

### 1. 后台运行

```bash
# 启动监控后按 Ctrl+Z，然后：
bg
disown

# 查看日志文件监控输出
tail -f ./logs/netfilter_trace_*.log
```

### 2. 与 tcpdump 结合

```bash
# 终端1：启动 netfilter_wrapper
./netfilter_wrapper.sh

# 终端2：同时抓包验证
sudo tcpdump -i any host 192.168.1.100
```

### 3. 定时监控

```bash
# 使用 cron 定期运行
crontab -e

# 每天凌晨3点运行5分钟，保存日志
0 3 * * * cd /path/to/learnebpf/毕设 && timeout 300 ./netfilter_wrapper.sh
```

### 4. 日志分析脚本

```bash
# 统计各类包的数量
cat ./logs/*.log | awk '
/\[ACCEPT\]/ {accept++}
/\[DROP\]/   {drop++}
/\[OTHER=/   {other++}
END {
    print "ACCEPT:", accept
    print "DROP:  ", drop
    print "OTHER: ", other
}'
```

## 与直接运行 bpftrace 的区别

| 特性 | 直接运行 bpftrace | 使用 wrapper |
|------|-------------------|--------------|
| 过滤能力 | 需要修改脚本 | 交互式设置 |
| 日志保存 | 手动重定向 | 自动管理 |
| 易用性 | 需要记住参数 | 菜单选择 |
| 组合过滤 | 复杂 | 简单 |
| 动态调整 | 需要重启 | 重新选择即可 |

## 总结

`netfilter_wrapper.sh` 提供了：
- 🎯 **精准过滤** - 只看你想看的
- 📝 **自动日志** - 无缝记录和查询
- 🖥️ **友好界面** - 无需记忆参数
- 🔧 **灵活组合** - 多条件同时生效

适合日常网络调试、安全审计、性能分析等场景。
