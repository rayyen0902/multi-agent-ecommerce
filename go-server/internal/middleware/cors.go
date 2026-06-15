package middleware

import (
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// corsOrigins 从环境变量读取允许的 CORS 来源
func corsOrigins() []string {
	origins := os.Getenv("CORS_ORIGINS")
	if origins == "" {
		return []string{"http://localhost:3000", "http://localhost:80", "http://localhost:5173"}
	}
	result := make([]string, 0)
	for _, o := range strings.Split(origins, ",") {
		o = strings.TrimSpace(o)
		if o != "" {
			result = append(result, o)
		}
	}
	return result
}

// CorsMiddleware 跨域中间件 — 仅允许配置中的来源
func CorsMiddleware() gin.HandlerFunc {
	allowedOrigins := corsOrigins()

	return func(c *gin.Context) {
		origin := c.GetHeader("Origin")

		// 检查请求来源是否在白名单中
		allowed := false
		for _, o := range allowedOrigins {
			if origin == strings.TrimSpace(o) {
				c.Header("Access-Control-Allow-Origin", origin)
				c.Header("Access-Control-Allow-Credentials", "true")
				allowed = true
				break
			}
		}

		if !allowed {
			// 不允许的来源 — 直接拒绝
			c.AbortWithStatus(http.StatusForbidden)
			return
		}

		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization, Accept, X-Requested-With")
		c.Header("Access-Control-Expose-Headers", "Content-Length, Content-Disposition")
		c.Header("Access-Control-Max-Age", "86400")

		if c.Request.Method == http.MethodOptions {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	}
}

// LoggerMiddleware 请求日志中间件
func LoggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method

		c.Next()

		latency := time.Since(start)
		statusCode := c.Writer.Status()

		gin.DefaultWriter.Write([]byte(
			"[GIN] " + time.Now().Format("2006/01/02 - 15:04:05") +
				" | " + method +
				" | " + path +
				" | " + c.ClientIP() +
				" | " + http.StatusText(statusCode) +
				" | " + latency.String() + "\n",
		))
	}
}
