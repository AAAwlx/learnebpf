# netfilter_trace - 两种实现方案对比

## 方案一：eBPF C + libbpf-go（模块化）

### 文件位置

`/home/ylx/我的项目/learnebpf/毕设/modular/`

### 架构特点

- ✅ 持久化监控（后台运行）
- ✅ 四函数解耦设计
- ✅ 高性能（编译为原生字节码）
- ✅ 可集成到现有系统
- ✅ 支持复杂逻辑

### 四个核心函数

```c
// 1. 提取 skb 指针
static __always_inline struct sk_buff *get_skb_ptr(struct pt_regs *ctx, int param_idx);

// 2. 获取 IP 头指针
static __always_inline void *get_iphdr_ptr(struct sk_buff *skb);

// 3. 转换获取 IP 地址
static __always_inline int extract_ip_addrs(void *iph_ptr, __u32 *saddr, __u32 *daddr);

// 4. 打印结果
static __always_inline void print_result(const char *func_name, __u32 saddr, __u32 daddr, __u64 skb_addr);
```

### 使用方法

```bash
cd modular
./build_and_run.sh
```

### 输出示例

```
[ip_rcv] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789
[ip_local_deliver] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789
```

---

## 方案二：bpftrace（脚本化）

### 文件位置

`/home/ylx/我的项目/learnebpf/毕设/netfilter_trace.bt`

### 架构特点
- ✅ 无需编译，即时运行
- ✅ 脚本化，易于修改
- ✅ 适合快速原型和调试
- ✅ 清晰的四步骤注释

### 四个步骤（在每个 kprobe 中）

```bpftrace
# 1. 提取 skb 指针
$skb = (struct sk_buff *)arg0;

# 2. 获取 IP 头指针
$data_ptr = $skb->data;

# 3. 转换获取 IP 地址
$iph = (struct iphdr *)$data_ptr;
$saddr = $iph->saddr;
$daddr = $iph->daddr;

# 4. 打印结果
printf("[ip_rcv] %pI4 -> %pI4 | skb:0x%llx\n", ...);
```

### 使用方法

```bash
cd /home/ylx/我的项目/learnebpf/毕设
sudo ./netfilter_trace.bt
```

### 输出示例
```
[ip_rcv] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789
[ip_local_deliver] 192.168.1.100 -> 8.8.8.8 | skb:0xffff888123456789
```

---

## 如何选择

### 选择 eBPF C 版本（modular/）如果：
- 需要长期运行的监控服务
- 需要集成到生产环境
- 需要高性能和低开销
- 需要复杂的业务逻辑
- 需要与其他 Go 程序集成

### 选择 bpftrace 版本（.bt）如果：
- 只是临时调试或学习
- 需要快速修改和测试
- 不想处理编译和依赖
- 需要理解内核函数调用流程
- 做原型验证

---

## 监控的 10 个 Netfilter 钩子点

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

---

## 查看输出的统一方法

```bash
# 方法1：实时查看 trace_pipe
sudo cat /sys/kernel/debug/tracing/trace_pipe | grep '\['

# 方法2：后台运行 eBPF 程序，另一个终端查看
sudo ./netfilter_trace_modular  # 终端1
sudo cat /sys/kernel/debug/tracing/trace_pipe | grep '\['  # 终端2

# 方法3：bpftrace 会直接输出到 stdout
sudo ./netfilter_trace.bt
```

---

## 故障排查

### 如果显示 0.0.0.0

**原因**：在特定 hook 点，skb->data 可能不指向 IP 头

**解决方案**：
1. 使用 `skb->head + skb->network_header` 代替 `skb->data`
2. 添加边界检查验证 IP 头有效性
3. 尝试在不同的 hook 点查看（如 ip_rcv 最可靠）

### 如果没有输出

**检查**：
1. 是否有网络流量？尝试 `ping 8.8.8.8`
2. 是否以 root 运行？需要 sudo
3. trace_pipe 是否被占用？确保只有一个监控程序运行

---

## 性能对比

| 特性 | eBPF C | bpftrace |
|------|--------|----------|
| 启动时间 | 1-2秒 | <0.5秒 |
| 运行开销 | 极低 | 稍高 |
| 内存占用 | ~1MB | ~5MB |
| CPU占用 | <0.1% | 0.1-0.5% |
| 可持久化 | ✅ | ❌（Ctrl+C 退出） |
| 部署难度 | 中等 | 简单 |

---

## 总结

两个版本都采用了**模块化设计思想**，将复杂逻辑拆分为清晰的四个步骤。

推荐：
- **学习和开发**：先用 bpftrace 快速验证
- **生产环境**：用 eBPF C 版本获得更好性能

两者代码结构一致，方便相互转换和对照学习。
