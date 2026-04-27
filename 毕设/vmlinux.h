/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
#ifndef __VMLINUX_H__
#define __VMLINUX_H__

#include <linux/types.h>

// 前向声明
struct sk_buff;

// pt_regs 结构定义 (x86_64)
// 参考：arch/x86/include/asm/ptrace.h
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
} __attribute__((preserve_access_index));

#endif /* __VMLINUX_H__ */
