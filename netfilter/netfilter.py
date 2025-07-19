#!/usr/bin/env python3
from bcc import BPF
import ctypes
import sys
from collections import defaultdict

class IpEvent(ctypes.Structure):
    _fields_ = [
        ("skbaddr", ctypes.c_ulonglong),
        ("saddr", ctypes.c_uint),
        ("daddr", ctypes.c_uint),
        ("chain_flag", ctypes.c_ubyte),
        ("ts", ctypes.c_ulonglong),
        ("funcname", ctypes.c_char * 32)
    ]

# Netfilter 链标志定义
chain_flags = {
    0x00:"NF_NULL",
    0x01: "NF_PRE_ROUTING",
    0x02: "NF_LOCAL_IN",
    0x08: "NF_FORWARD",
    0x10: "NF_LOCAL_OUT",
    0x20: "NF_POST_ROUTING"
}

# 全局存储跟踪数据
skb_tracker = defaultdict(list)

b = BPF(src_file="netfilter.c")

# 定义出口函数（触发完整链路打印）
EXIT_FUNCTIONS = {
    b"ip_local_deliver_finish",
    b"ip_finish_output"
}

functions = [
    ("ip_rcv", "trace_ip_rcv"),
    ("ip_rcv_finish", "trace_ip_rcv_finish"),
    ("ip_local_deliver", "trace_ip_local_deliver"),
    ("ip_local_deliver_finish", "trace_ip_local_deliver_finish"),
    ("ip_local_out", "trace_ip_local_out"),
    ("ip_forward", "trace_ip_forward"),
    ("ip_mr_forward", "trace_ip_mr_forward"),
    ("ip_output", "trace_ip_output"),
    ("ip_mc_output", "trace_ip_mc_output"),
    ("ip_finish_output", "trace_ip_finish_output"),
]

for func, probe in functions:
    try:
        b.attach_kprobe(event=func, fn_name=probe)
        print(f"Attached probe to {func}")
    except Exception as e:
        print(f"Failed to attach to {func}: {str(e)}")

def reverse_ip_bytes(ip_int):
    """将网络序IP转换为点分十进制"""
    return ((ip_int & 0xFF) << 24) | \
           ((ip_int & 0xFF00) << 8) | \
           ((ip_int >> 8) & 0xFF00) | \
           ((ip_int >> 24) & 0xFF)

def ip_to_str(ip_int):
    reversed_ip = reverse_ip_bytes(ip_int)
    return f"{(reversed_ip >> 24) & 0xff}.{(reversed_ip >> 16) & 0xff}.{(reversed_ip >> 8) & 0xff}.{reversed_ip & 0xff}"

def print_skb_chain(skbaddr, events):
    """打印单个SKB的完整处理链路"""
    first = events[0]
    print(f"\n[SKB 0x{skbaddr:x}] {ip_to_str(first.saddr)} -> {ip_to_str(first.daddr)}")
    
    # 合并所有链标志
    chains = {chain_flags.get(e.chain_flag, "UNKNOWN") for e in events}
    print("Behavior Chain:", " -> ".join(chains))
    
    # 打印函数调用序列
    print("Function Trace:")
    prev_ts = None
    for i, event in enumerate(events, 1):
        func_name = event.funcname.decode('ascii', errors='replace').strip()
        delta = (event.ts - prev_ts)/1e6 if prev_ts else 0
        print(f"  [{i}] {func_name:<20} | TS: {event.ts} | Δ: {delta:.3f} ms")
        prev_ts = event.ts

def process_event(cpu, data, size):
    """处理单个事件"""
    event = ctypes.cast(data, ctypes.POINTER(IpEvent)).contents
    skbaddr = event.skbaddr
    skb_tracker[skbaddr].append(event)
    
    # 检查是否为出口函数
    if event.funcname in EXIT_FUNCTIONS:
        if skbaddr in skb_tracker:
            print_skb_chain(skbaddr, skb_tracker[skbaddr])
            del skb_tracker[skbaddr]  # 删除已处理的记录

def print_final_report():
    """程序退出时打印剩余未完成的数据包"""
    if skb_tracker:
        print("\n=== Remaining Packets ===")
        for skbaddr, events in skb_tracker.items():
            print_skb_chain(skbaddr, events)

b["ip_events"].open_perf_buffer(process_event)

print("Tracing IP packet processing... Ctrl+C to exit")
try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    print_final_report()
    for func, _ in functions:
        try:
            b.detach_kprobe(event=func)
        except:
            pass
    sys.exit(0)

