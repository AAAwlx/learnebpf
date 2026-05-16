/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
#ifndef __VMLINUX_H__
#define __VMLINUX_H__

#include <linux/types.h>

// IP 头部结构
struct iphdr {
    __u8    ihl:4, version:4;
    __u8    tos;
    __u16   tot_len;
    __u16   id;
    __u16   frag_off;
    __u8    ttl;
    __u8    protocol;
    __u16   check;
    __be32  saddr;
    __be32  daddr;
};

// Socket buffer 结构（简化版 - 只包含我们需要字段）
struct sk_buff {
    __u64 reserved[8];
    void *data;           // 数据指针（直接指向网络包数据）
    void *head;
    __u16 network_header;
    __u16 transport_header;
};

// pt_regs 结构定义 (x86_64)
struct pt_regs {
    __u64 r15;
    __u64 r14;
    __u64 r13;
    __u64 r12;
    __u64 bp;
    __u64 bx;
    __u64 r11;
    __u64 r10;
    __u64 r9;
    __u64 r8;
    __u64 ax;
    __u64 cx;
    __u64 dx;
    __u64 si;
    __u64 di;
    __u64 orig_ax;
    __u64 ip;
    __u64 cs;
    __u64 flags;
    __u64 sp;
    __u64 ss;
};

#endif /* __VMLINUX_H__ */
