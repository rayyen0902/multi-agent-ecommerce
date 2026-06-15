package middleware

import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/model"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
)

const ContextUserIDKey = "user_id"
const ContextUsernameKey = "username"
const ContextRoleKey = "role"

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
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
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
func AuthMiddleware(secret string, db *gorm.DB) gin.HandlerFunc {
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

		// 从数据库加载用户角色和 shop_id
		var user model.User
		if err := db.Select("role", "shop_id").First(&user, claims.UserID).Error; err != nil {
			pkg.FailWithStatus(c, http.StatusUnauthorized, pkg.ErrCodeUnauthorized, "用户不存在")
			c.Abort()
			return
		}

		c.Set(ContextUserIDKey, claims.UserID)
		c.Set(ContextUsernameKey, claims.Username)
		c.Set(ContextRoleKey, user.Role)
		c.Next()
	}
}
