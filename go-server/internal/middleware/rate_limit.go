package middleware

import (
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
)

// rateLimitStore 简单的内存限速器
type rateLimitStore struct {
	mu       sync.Mutex
	requests map[string][]time.Time
	limit    int
	window   time.Duration
}

var limiter = &rateLimitStore{
	requests: make(map[string][]time.Time),
	limit:    10,
	window:   15 * time.Minute,
}

func (r *rateLimitStore) allow(key string) bool {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-r.window)

	// 清理过期记录
	timestamps := r.requests[key]
	valid := timestamps[:0]
	for _, ts := range timestamps {
		if ts.After(windowStart) {
			valid = append(valid, ts)
		}
	}

	if len(timestamps) >= r.limit {
		r.requests[key] = valid
		return false
	}

	r.requests[key] = append(valid, now)
	return true
}

// LoginRateLimit 登录接口速率限制中间件
// 15 分钟内最多允许 10 次请求
func LoginRateLimit() gin.HandlerFunc {
	return func(c *gin.Context) {
		clientIP := c.ClientIP()
		if !limiter.allow(clientIP) {
			pkg.FailWithStatus(c, 429, 429, "请求过于频繁，请稍后再试")
			c.Abort()
			return
		}
		c.Next()
	}
}
