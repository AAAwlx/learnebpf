package main

import(
	"net/http"
    "github.com/gin-gonic/gin"
)

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
	router.GET("/netcap", func(c *gin.Context) {
		c.HTML(http.StatusOK, "milaoshu.html", nil) // 加载 milaoshu.html 文件，后面改为
	})

	router.POST("/netcap", )//处理参数请求ebpf
	
	router.Run(":8000")
}

func loginEndpoint(c *gin.Context){
	// 登录逻辑，这里暂时为空
	// 假设登录成功，重定向到 /netcap
	c.Redirect(http.StatusFound, "/netcap")
}
