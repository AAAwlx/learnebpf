package cmd

import(
	"fmt"
	//"context"
	//"log"
	"os"      // 导入 os 包以便进行文件操作
    "os/exec" // 导入 exec 包以执行外部命令
    "net/http"
	"github.com/gin-gonic/gin"
	//"skb/dump"
)

// 请求参数结构体
type CommandRequest struct {
    Buffermod         string `json:"Buffermod"`         // 包类型 (skb, mbuf, raw)
    Filter            string `json:"filter"`            // -f 参数，指定需要 trace 的函数名称
    Expression        string `json:"expression"`        // -e 参数，数据包过滤表达式
    TcpdumpOpts       string `json:"tcpdump_options"`   // -t 参数，tcpdump flags
    WriteFile         string `json:"write_file"`        // -w 参数，输出文件名
	WriteFileRotate   uint32 `json:"write_file_rotate"`								// 选择循环覆盖写的方式，当超过由此参数指定的
    CaptureCount      uint32    `json:"capture_count"`     // -c 参数，捕获包数量
    CaptureMaxSize    uint32    `json:"capture_max_size"`  // --capture-max-size 参数，捕获包的最大大小
    UserFilter        string `json:"user_filter"`       // --user-filter 参数，用户自定义 filter 文件
    UserAction        string `json:"user_action"`       // --user-action 参数，用户自定义 action 文件
    DryRun            bool   `json:"dry_run"`           // --dry-run 参数，是否只生成代码而不执行
}
//向前端返回的josn格式
type TCPHeader struct {
	SourcePort      int    `json:"source_port"`
	DestinationPort int    `json:"destination_port"`
	SequenceNumber  int    `json:"sequence_number"`
	AckNumber       int    `json:"ack_number"`
	DataOffset      int    `json:"data_offset"`
	Flags           string `json:"flags"`
	WindowSize      int    `json:"window_size"`
}

func Execute(c *gin.Context) {
	var cmdRequest CommandRequest
	
	// 解析请求的 JSON 数据
	if err := c.ShouldBindJSON(&cmdRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
    }
	if cmdRequest.Buffermod == "skb" {//skb包
		go doSkbDumap(&cmdRequest)
        c.Redirect(http.StatusFound, "/tcp_headers")
		//c.JSON(http.StatusOK, gin.H{"result": "skb get"})
		return
	}else if cmdRequest.Buffermod == "raw"{//raw包
		//doRawDumap(&cmdRequest)
		c.JSON(http.StatusOK, gin.H{"result": "raw get"})
		return
	}else if cmdRequest.Buffermod == "mbuf" {//mbuf包
		//doMbufDump(&cmdRequest)
		c.JSON(http.StatusOK, gin.H{"result": "mbuf get"})
		return
	}else{
		c.JSON(http.StatusInternalServerError, gin.H{"error": "参数不合规"})	
		return
	}
	// 返回结果
	//c.JSON(http.StatusOK, gin.H{"result": "succed"})
}

//func commOption(c *CommandRequest) *dump.Option {
//	opt := &dump.Option{
//		UserFilterFilePath:         c.UserFilter,//用户自定义 filter （过滤器）文件所在的路径
//		UserActionFilePath:         c.UserAction,//用户自定义的 Action 文件所在的路径
//		TcpdumpFlags:               c.TcpdumpOpts,//设置tcpdump的参数
//		TcpdumpExpression:          c.Expression,//数据包表达式
//		TraceFunction:              c.Filter,//挂载方法与挂载函数名
//		DumpWriteFilePath:          c.WriteFile,//转储写入文件的路径
//		DumpWriteFileRotate:        c.WriteFileRotate,//文件尺寸，超过后覆盖写
//		DumpCount:                  c.CaptureCount,//抓到包的数量，超过该数量后的包将不再抓取
//		CaptureMaxSize:             c.CaptureMaxSize,//这个size是指抓的包，保存到buff的大小，如果包长超过这个值，则包会被截断
//		IsDryRun:                   c.DryRun,
//	}
//
//	return opt
//}
//
//// runDump 函数执行给定的 dump.Operator 操作
//func runDump(dumpOp dump.Operator) {
//    // 调用 dumpOperator 的 Run 方法，使用一个背景上下文
//    err := dumpOp.Run(context.TODO())
//    if err != nil {
//        // 如果发生错误，则记录错误并终止程序
//        log.Fatalf("Dump operator run err: %v", err)
//    }
//}

func doSkbDumap(c *CommandRequest){
	cmdPath := "/home/ylx/bpf-developer-tutorial/src/41-xdp-tcpdump/xdp-tcpdump"
    
    // 打开文件进行写入（如果文件不存在则创建）
    outputFile, err := os.Create("/home/ylx/我的项目/skb/skb.txt")
    if err != nil {
        fmt.Println("Error creating output file:", err)
        return
    }
    defer outputFile.Close() // 确保程序退出时关闭文件

    // 创建一个 exec.Command 对象，使用 sudo 运行命令
    cmd := exec.Command("sudo", cmdPath, "wlan0") // 使用 sudo 来运行需要特权的命令

    // 设置命令的输出重定向到文件
    cmd.Stdout = outputFile  // 标准输出重定向到文件
    cmd.Stderr = outputFile  // 标准错误也重定向到文件

    // 运行命令
    err = cmd.Run()
    if err != nil {
        fmt.Println("Error executing command:", err)
        return
    }

    fmt.Println("Command output has been written to /home/ylx/我的项目/skb/skb.txt")
}

//func doRawDumap(c *CommandRequest){

//}

//func doMbufDump(c *CommandRequest){
	
//}