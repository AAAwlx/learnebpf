#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <linux/ip.h>

#define MAX_FUNCS 10  // 最大跟踪函数数量
#define MAX_FUNC_NAME_LEN 64  // 函数名最大长度

#define NF_NULL 0
#define NF_PRE_ROUTING 1
#define NF_LOCAL_IN 2
#define NF_FORWARD 8
#define NF_LOCAL_OUT 16
#define NF_POST_ROUTING 32

// 传输到用户空间的结构体
struct ip_event_t {
    u64 skbaddr;    // skb地址（用于关联）
    u32 saddr;
    u32 daddr; // 源IP和目的IP
    u8 chain_flag; // 经过的行为链 
    u64 ts; // 时间戳
    char funcname [MAX_FUNC_NAME_LEN]; // 函数名数组
};

BPF_PERF_OUTPUT(ip_events);                   // 输出通道

// 协议栈通用记录函数
static int record_func(struct pt_regs *ctx, struct sk_buff *skb, u8 chain_flag, const char *name) {
    // 安全检查
    void *data = (void *)(long)skb->data;
    //void *data_len = (void *)(long)skb->data_len;
    //if (data + sizeof(struct iphdr) > data_len) return 0;

    struct iphdr *ip = data;
    struct ip_event_t event = {};
    memset(event.funcname, 0, sizeof(event.funcname));
    // 填充基础字段
    event.skbaddr = (u64)skb;
    event.saddr = ip->saddr;
    event.daddr = ip->daddr;
    event.chain_flag = chain_flag;
    event.ts = bpf_ktime_get_ns();
    
    //u64 func_ip = PT_REGS_IP(ctx);

    // 安全复制函数名
    bpf_probe_read_kernel_str(event.funcname, sizeof(event.funcname), name);
    bpf_trace_printk("skb1:0x%llx Event submitted: %s time: %llu\n", (u64)skb, event.funcname, event.ts);
    
    // 提交事件
    ip_events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}

// Netfilter钩子函数跟踪


// 各挂载点处理函数
int trace_ip_rcv(struct pt_regs *ctx, struct sk_buff *skb) {
    char name[MAX_FUNC_NAME_LEN] = "ip_rcv";
    record_func(ctx, skb, NF_PRE_ROUTING, name);
    return 0;
}

int trace_ip_rcv_finish(struct pt_regs *ctx) {

    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM3(ctx);  // arg3 = %rdx
    bpf_trace_printk("ip_rcv_finish");
    char name[MAX_FUNC_NAME_LEN] = "ip_rcv_finish";
    record_func(ctx, skb, NF_NULL, name);
    return 0;
}

int trace_ip_local_deliver(struct pt_regs *ctx, struct sk_buff *skb) {
    char name[MAX_FUNC_NAME_LEN] = "ip_local_deliver";
    record_func(ctx, skb, NF_LOCAL_IN, name);
    return 0;
}

int trace_ip_local_deliver_finish(struct pt_regs *ctx) {
    char name[MAX_FUNC_NAME_LEN] = "ip_local_deliver_finish";
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM3(ctx); 
    record_func(ctx, skb, NF_NULL, name);
    return 0;
}

int trace_ip_forward(struct pt_regs *ctx, struct sk_buff *skb) {
    char name[MAX_FUNC_NAME_LEN] = "ip_forward";
    record_func(ctx, skb, NF_FORWARD, name);
    return 0;
}

int trace_ip_mr_forward(struct pt_regs *ctx) {
    char name[MAX_FUNC_NAME_LEN] = "ip_mr_forward";
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM4(ctx);
    record_func(ctx, skb, NF_FORWARD, name);
    return 0;
}


int trace_ip_local_out(struct pt_regs *ctx) {
    char name[MAX_FUNC_NAME_LEN] = "ip_local_out";
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM3(ctx);
    record_func(ctx, skb, NF_LOCAL_OUT, name);
    return 0;
}

int trace_ip_output(struct pt_regs *ctx) {
    char name[MAX_FUNC_NAME_LEN] = "ip_output";
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM3(ctx);
    record_func(ctx, skb, NF_POST_ROUTING, name);
    return 0;
}

int trace_ip_mc_output(struct pt_regs *ctx) {
    char name[MAX_FUNC_NAME_LEN] = "ip_mc_output";
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM3(ctx);
    record_func(ctx, skb, NF_POST_ROUTING, name);
    return 0;
}

int trace_ip_finish_output(struct pt_regs *ctx) {
    char name[MAX_FUNC_NAME_LEN] = "ip_finish_output";
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM3(ctx);  // arg3 = %rdx
    record_func(ctx, skb, NF_NULL, name);        
    return 0;
}