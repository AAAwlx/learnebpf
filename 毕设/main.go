package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/cilium/ebpf"
	"github.com/cilium/ebpf/link"
	"github.com/cilium/ebpf/rlimit"
)

func main() {
	// 设置信号处理
	stopper := make(chan os.Signal, 1)
	signal.Notify(stopper, os.Interrupt, syscall.SIGTERM)

	// 移除内存限制
	if err := rlimit.RemoveMemlock(); err != nil {
		log.Fatalf("Failed to remove memory lock: %v", err)
	}

	// 加载预编译的 BPF 程序
	objs := netfilter_traceObjects{}
	if err := loadNetfilter_traceObjects(&objs, nil); err != nil {
		log.Fatalf("Failed to load BPF objects: %v", err)
	}
	defer objs.Close()

	// 附加所有 kprobe
	kprobes := []struct {
		name string
		prog *ebpf.Program
	}{
		{"ip_rcv", objs.KprobeIpRcv},
		{"ip_rcv_finish", objs.KprobeIpRcvFinish},
		{"ip_local_deliver", objs.KprobeIpLocalDeliver},
		{"ip_local_deliver_finish", objs.KprobeIpLocalDeliverFinish},
		{"ip_forward", objs.KprobeIpForward},
		{"ip_mr_forward", objs.KprobeIpMrForward},
		{"ip_local_out", objs.KprobeIpLocalOut},
		{"ip_output", objs.KprobeIpOutput},
		{"ip_mc_output", objs.KprobeIpMcOutput},
		{"ip_finish_output", objs.KprobeIpFinishOutput},
	}

	attachedCount := 0
	for _, kp := range kprobes {
		link, err := link.Kprobe(kp.name, kp.prog, nil)
		if err != nil {
			log.Printf("Warning: Failed to attach kprobe %s: %v", kp.name, err)
			continue
		}
		defer link.Close()
		attachedCount++
		log.Printf("✓ Attached kprobe: %s", kp.name)
	}

	if attachedCount == 0 {
		log.Fatal("Failed to attach any kprobes")
	}

	log.Printf("\n========================================")
	log.Printf("Netfilter Trace Monitor Started!")
	log.Printf("Attached %d kprobes successfully", attachedCount)
	log.Printf("========================================\n")
	log.Printf("View kernel output with:")
	log.Printf("  sudo cat /sys/kernel/debug/tracing/trace_pipe")
	log.Printf("\nOr filter for our output:")
	log.Printf("  sudo cat /sys/kernel/debug/tracing/trace_pipe | grep 'Function:'")
	log.Printf("\nPress Ctrl+C to stop...\n")

	// 等待信号
	<-stopper
	log.Println("\nReceived signal, exiting program..")
}
