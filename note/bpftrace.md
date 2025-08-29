# bpftrace

### bpftrace 常用命令

---

### 📌 基础操作

```bash
bpftrace -l                # 列出所有可用的探针
bpftrace -lv kprobe:tcp_*  # 查看 tcp_* 相关的内核函数探针详情
bpftrace -e 'tracepoint:syscalls:sys_enter_* { printf("%s\n", probe); }'
                           # 跟踪所有系统调用入口
```

---

### 📌 系统调用监控

```bash
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("open %s\n", str(args->filename)); }'
                           # 跟踪文件打开
bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("exec: %s\n", str(args->filename)); }'
                           # 跟踪进程执行
bpftrace -e 'tracepoint:syscalls:sys_enter_clone { printf("clone pid=%d\n", pid); }'
                           # 跟踪进程创建
```

---

### 📌 函数耗时分析

```bash
bpftrace -e '
kprobe:do_sys_open { @start[tid] = nsecs; }
kretprobe:do_sys_open /@start[tid]/ {
    @delta = hist(nsecs - @start[tid]);
    delete(@start[tid]);
}'
                           # 分析 open() 系统调用耗时直方图
```

---

### 📌 CPU / 调度分析

```bash
bpftrace -e 'tracepoint:sched:sched_switch { printf("%d -> %d\n", args->prev_pid, args->next_pid); }'
                           # 打印进程调度切换
bpftrace -e 'profile:hz:99 { @[cpu] = count(); }'
                           # 统计每个 CPU 的采样事件，反映负载分布
```

---

### 📌 内存与 I/O

```bash
bpftrace -e 'tracepoint:kmem:kmalloc { @bytes = hist(args->bytes_alloc); }'
                           # 统计 kmalloc 分配大小分布
bpftrace -e 'tracepoint:block:block_rq_issue { printf("Disk I/O: %d bytes\n", args->bytes); }'
                           # 跟踪块设备 I/O 请求
```

---

### 📌 网络监控

```bash
bpftrace -e 'tracepoint:net:netif_receive_skb { @[comm] = count(); }'
                           # 统计收到包的进程
bpftrace -e 'tracepoint:syscalls:sys_enter_sendto { @[pid, comm] = count(); }'
                           # 跟踪 sendto 调用次数
bpftrace -e 'tracepoint:tcp:tcp_retransmit_skb { @[comm] = count(); }'
                           # 统计 TCP 重传
```

---

### 📌 热函数 / 火焰图准备

```bash
bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'
                           # 内核栈采样
bpftrace -e 'profile:hz:99 { @[ustack] = count(); }'
                           # 用户态栈采样
```

---
sudo bpftrace -e 'kprobe:vfs_read { @[kstack] = count(); }'

### 📌 调试小技巧

```bash
bpftrace -e 'BEGIN { printf("Tracing... Hit Ctrl-C to end.\n"); }'
bpftrace -e 'END { print(@); }'
                           # 程序开始和结束时执行
```

---

### 打印函数调用栈

```bash
sudo bpftrace -e 'kprobe:vfs_read { @[kstack] = count(); }'
```

---

✅ 总结：

* `tracepoint:*` → 适合观测系统事件（系统调用、网络、块设备等）。
* `kprobe:/kretprobe:` → 动态跟踪函数入口/返回。
* `profile:hz:N` → 周期性采样（性能分析）。
* `hist() / count() / sum() / avg()` 等聚合函数用于分析分布与统计。

---
