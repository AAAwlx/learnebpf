package cmd

import(
	//"fmt"
    "net/http"
	"github.com/gin-gonic/gin"
)

// 请求参数结构体
type CommandRequest struct {
	Buffermod string `json:"buffermod"`//包类型，skb/mbuf/raw
    Command string `json:"command"`
}

func Execute(c *gin.Context) {
	var cmdRequest CommandRequest
	
    // 解析请求的 JSON 数据
    if err := c.ShouldBindJSON(&cmdRequest); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
	if cmdRequest.Buffermod == "skb" {//skb包
        
		c.JSON(http.StatusOK, gin.H{"result": "skb get"})
        return
	}else if cmdRequest.Buffermod == "raw"{//raw包
		c.JSON(http.StatusOK, gin.H{"result": "raw get"})
        return
	}else if cmdRequest.Buffermod == "mbuf" {//mbuf包
		c.JSON(http.StatusOK, gin.H{"result": "mbuf get"})
        return
	}else{
        c.JSON(http.StatusInternalServerError, gin.H{"error": "参数不合规"})
        return
    }
    // 返回结果
    //c.JSON(http.StatusOK, gin.H{"result": "succed"})
}

