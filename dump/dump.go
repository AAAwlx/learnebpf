package dump

//import(
//	"context"
//	"skb/dump/driver"
//)
//
//type Operator interface {
//	Run(ctx context.Context) error
//}
//
////通用选项参数的值
//type Option struct {
//	UserFilterFilePath  string
//	UserActionFilePath  string
//	UserOutputColor     string
//	TcpdumpFlags        string
//	TcpdumpExpression   string
//	TraceFunction       string
//	DumpWriteFilePath   string
//	DumpWriteFileRotate uint32
//
//	DumpCount      uint32
//	CaptureMaxSize uint32
//
//	IsDryRun                   bool
//}
//
//// dumpBaseImpl 是一个结构体，包含了与 dump 操作相关的基础实现
//type dumpBaseImpl struct {
//    driver driver.Operator      // 驱动程序操作接口，用于与底层驱动交互
//    //parser tparser.Operator     // 解析器操作接口，用于解析数据包或其他输入数据
//}
//