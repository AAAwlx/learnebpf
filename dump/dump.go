package dump

import(
	"context"
)

type Operator interface {
	Run(ctx context.Context) error
}

//各项参数的值
type Option struct {
	UserFilterFilePath  string
	UserActionFilePath  string
	UserOutputColor     string
	TcpdumpFlags        string
	TcpdumpExpression   string
	TraceFunction       string
	DumpWriteFilePath   string
	DumpWriteFileRotate uint32

	DumpCount      uint32
	CaptureMaxSize uint32

	IsDryRun                   bool
}


