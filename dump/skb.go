package dump

type SkbOption struct {
	Option

	Interface      string
	IsDumpStack    bool
	IsFakeHdr      bool
	IsUseSkbData   bool
	SkbDataOffset  int32
}

func NewSkbDump(opt *SkbOption) (Operator, error){

}