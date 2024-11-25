package driver

import(
	"context"
	"github.com/aquasecurity/libbpfgo" // 引入 libbpfgo 包
)

// Operator 接口定义了初始化和运行操作的基本方法
type Operator interface {
    Init() error                     // 初始化操作，返回错误（如果有）
    Run(ctx context.Context) error   // 执行操作，使用给定的上下文，返回错误（如果有）
}

// driverBaseImpl 结构体实现了与驱动程序相关的基础操作
type driverBaseImpl struct {
    m            *libbpfgo.Module         // BCC 模块，提供低级别的 BPF 功能
    //gather       gather.Operator      // 数据收集的操作接口
    //outputDriver output.Operator      // 输出操作接口，负责处理输出
    //extendOp     extend.Operator      // 扩展操作的接口
    perfChannel  chan []byte         // 性能数据通道，接收性能事件
    tickChannel  chan int            // 定时信号通道，用于触发定期操作
    maxDumpCount uint32              // 最大转储包数量限制

    dumpCount uint32                 // 当前转储包数量
}