#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

// 通用跟踪函数 - 直接在内核打印
static int trace_network_func(struct pt_regs *ctx, const char *func_name)
{
    // 直接读取 pt_regs 结构体成员
    // 对于 x86_64: di=参数1, si=参数2, dx=参数3, cx=参数4
    unsigned long long param1, param2, param3, param4;

    param1 = ctx->di;
    param2 = ctx->si;
    param3 = ctx->dx;
    param4 = ctx->cx;

    // 直接在内核打印
    bpf_printk("Function: %s | skb: 0x%llx | args: [0x%llx, 0x%llx, 0x%llx, 0x%llx]",
               func_name, param1, param1, param2, param3, param4);

    return 0;
}

// ============== IP 协议栈函数 kprobe ==============

SEC("kprobe/ip_rcv")
int kprobe_ip_rcv(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_rcv");
}

SEC("kprobe/ip_rcv_finish")
int kprobe_ip_rcv_finish(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_rcv_finish");
}

SEC("kprobe/ip_local_deliver")
int kprobe_ip_local_deliver(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_local_deliver");
}

SEC("kprobe/ip_local_deliver_finish")
int kprobe_ip_local_deliver_finish(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_local_deliver_finish");
}

SEC("kprobe/ip_forward")
int kprobe_ip_forward(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_forward");
}

SEC("kprobe/ip_mr_forward")
int kprobe_ip_mr_forward(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_mr_forward");
}

SEC("kprobe/ip_local_out")
int kprobe_ip_local_out(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_local_out");
}

SEC("kprobe/ip_output")
int kprobe_ip_output(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_output");
}

SEC("kprobe/ip_mc_output")
int kprobe_ip_mc_output(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_mc_output");
}

SEC("kprobe/ip_finish_output")
int kprobe_ip_finish_output(struct pt_regs *ctx)
{
    return trace_network_func(ctx, "ip_finish_output");
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
