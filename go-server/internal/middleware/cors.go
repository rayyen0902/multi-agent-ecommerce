package middleware

import (
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

func corsOrigins() []string {
	origins := os.Getenv("CORS_ORIGINS")
	if origins == "" {
		origins = "http://localhost:3000,http://localhost:80,http://localhost:5173,https://knownot.cc"
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

func CorsMiddleware() gin.HandlerFunc {
	allowedOrigins := corsOrigins()

	return func(c *gin.Context) {
		origin := c.GetHeader("Origin")

		if origin == "" {
			// 同源请求或服务间调用，跳过 CORS 检查
			c.Next()
			return
		}

		for _, o := range allowedOrigins {
			if origin == o {
				c.Header("Access-Control-Allow-Origin", origin)
				c.Header("Access-Control-Allow-Credentials", "true")
			}
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
