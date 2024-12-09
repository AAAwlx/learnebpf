package main

import (
	"fmt"
	"net/http"
	"skb/cmd"

	//"fmt"
	"github.com/gin-gonic/gin"
)

type TCPHeadera struct {
	SourcePort          int    `json:"source_port"`
	DestinationPort     int    `json:"destination_port"`
	SequenceNumber      uint32 `json:"sequence_number"`
	AcknowledgmentNumber uint32 `json:"ack_number"`
	DataOffset          int    `json:"data_offset"`
	Flags               string `json:"flags"`
	WindowSize          int    `json:"window_size"`
}


func main() {
	router := gin.Default()
	// 提供 static 目录下的静态文件
	router.Static("/static", "./static")

	// 一次性加载所有的 HTML 模板文件
	router.LoadHTMLGlob("page/*.html")

	// 欢迎界面
	router.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "hello.html", nil) // 加载 hello.html 文件
    })
	
	// 登录 POST 请求
	router.POST("/", loginEndpoint) 

	// 重定向到 netcap 页面
	router.GET("/SkbHandler", func(c *gin.Context) {
		c.HTML(http.StatusOK, "skbhandler.html", nil) // 加载 milaoshu.html 文件，后面改为
	})

	router.POST("/SkbHandler", skbstart)//处理参数请求ebpf
	
	router.GET("/tcp_headers", func(c *gin.Context) {
		handler(c)
		//c.JSON(http.StatusOK, gin.H{"result": "raw get"})
		//c.HTML(http.StatusOK, "tcp.html", nil)
	})


	router.Run(":8000")
}

func loginEndpoint(c *gin.Context){
	// 登录逻辑，这里暂时为空
	// 假设登录成功，重定向到 /netcap
	c.Redirect(http.StatusFound, "/SkbHandler")
}

//进入到参数解析模块
func skbstart (c *gin.Context){
	//c.Redirect(http.StatusFound, "/tcp_headers")
	cmd.Execute(c)
}

func handler(c *gin.Context) {
	headers, err := cmd.LoadTCPHeaders("tcp_data.txt")
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{
            "error": err.Error(),
        })
        return
    }
    // 设置响应为 JSON
	c.Header("Content-Type", "application/json")
	fmt.Print(headers);
    c.JSON(http.StatusOK, headers)
}