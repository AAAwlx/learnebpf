package dump

//skb模式抓包选项值
//type SkbOption struct {
//	Option                //通用参数
//
//	Interface      string // -i 参数，网络接口
//	IsDumpStack    bool   //是否输出调用栈
//	IsFakeHdr      bool   // --fake-hdr 参数，伪造 header
//	IsUseSkbData   bool   // --skb-data 参数，使用 skb 数据
//	SkbDataOffset  int32  // --skb-data-offset 参数，skb 数据偏移量
//}
//
//func NewSkbDump(opt *SkbOption) (Operator, error) {
//
//	s := &skbDumpImpl{}
//
//	err := s.baseInit(&opt.Option)
//	if err != nil {
//		return nil, err
//	}
//
//	skbOpt := &code.SkbOption{
//		Option: code.Option{
//			TcpdumpExpression:  opt.TcpdumpExpression,
//			UserFilterFilePath: opt.UserFilterFilePath,
//			UserActionFilePath: opt.UserActionFilePath,
//			CaptureMaxSize:     opt.CaptureMaxSize,
//			FunctionDesc:       s.parser.Get(),
//			IsDumpStack:        opt.IsDumpStack,
//		},
//		Interface:     opt.Interface,
//		IsFakeHdr:     opt.IsFakeHdr,
//		IsUseSkbData:  opt.IsUseSkbData,
//		SkbDataOffset: opt.SkbDataOffset,
//	}
//
//	skbCode, err := code.NewSkbCode(skbOpt)
//	if err != nil {
//		return nil, err
//	}
//	if opt.IsDryRun {
//		fmt.Printf("\n%s\n", skbCode.GetEbpfCode())
//		os.Exit(0)
//	}
//
//	driverOpt := &driver.SkbOption{
//		Option: *driverOption(&opt.Option, skbCode, opt.IsDumpStack, opt.DumpStackColor),
//	}
//	s.driver = driver.NewSkbDriver(driverOpt)
//
//	err = s.driver.Init()
//	if err != nil {
//		return nil, err
//	}
//
//	return s, nil
//}//
