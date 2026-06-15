package middleware

import (
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"

	"github.com/multi-agent-ecom/go-server/internal/pkg"
)

const ContextUserIDKey = "user_id"
const ContextUsernameKey = "username"

type Claims struct {
	UserID   int64  `json:"user_id"`
	Username string `json:"username"`
	jwt.RegisteredClaims
}

func GenerateToken(userID int64, username, secret string, expireHour int) (string, int64) {
	expireAt := time.Now().Add(time.Duration(expireHour) * time.Hour).Unix()
	claims := Claims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Unix(expireAt, 0)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "multi-agent-ecom",
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenStr, _ := token.SignedString([]byte(secret))
	return tokenStr, expireAt
}

func ParseToken(tokenStr, secret string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		return []byte(secret), nil
	})
	if err != nil {
		return nil, err
	}
	if claims, ok := token.Claims.(*Claims); ok && token.Valid {
		return claims, nil
	}
	return nil, jwt.ErrSignatureInvalid
}

// AuthMiddleware JWT 鉴权中间件
func AuthMiddleware(secret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			pkg.FailWithStatus(c, http.StatusUnauthorized, pkg.ErrCodeUnauthorized, "缺少 Authorization 头")
			c.Abort()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			pkg.FailWithStatus(c, http.StatusUnauthorized, pkg.ErrCodeUnauthorized, "Authorization 格式错误")
			c.Abort()
			return
		}

		claims, err := ParseToken(parts[1], secret)
		if err != nil {
			pkg.FailWithStatus(c, http.StatusUnauthorized, pkg.ErrCodeTokenExpired, "Token 无效或已过期")
			c.Abort()
			return
		}

		c.Set(ContextUserIDKey, claims.UserID)
		c.Set(ContextUsernameKey, claims.Username)
		c.Next()
	}
}
