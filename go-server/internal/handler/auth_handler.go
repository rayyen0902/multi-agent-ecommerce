package handler

import (
	"errors"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/dto"
	"github.com/multi-agent-ecom/go-server/internal/middleware"
	"github.com/multi-agent-ecom/go-server/internal/model"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
)

type AuthHandler struct {
	db         *gorm.DB
	jwtSecret  string
	expireHour int
}

func NewAuthHandler(db *gorm.DB, jwtSecret string, expireHour int) *AuthHandler {
	return &AuthHandler{db: db, jwtSecret: jwtSecret, expireHour: expireHour}
}

func (h *AuthHandler) Login(c *gin.Context) {
	var req dto.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	var user model.User
	if err := h.db.Where("username = ?", req.Username).First(&user).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			pkg.Fail(c, pkg.ErrCodeUnauthorized, "用户名或密码错误")
			return
		}
		pkg.Fail(c, pkg.ErrCodeServerInternal, "服务器错误")
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		pkg.Fail(c, pkg.ErrCodeUnauthorized, "用户名或密码错误")
		return
	}

	if user.Status != 1 {
		pkg.Fail(c, pkg.ErrCodeForbidden, "账号已被禁用")
		return
	}

	token, expireAt := middleware.GenerateToken(user.ID, user.Username, h.jwtSecret, h.expireHour)

	// 更新最后登录时间
	now := time.Now()
	h.db.Model(&user).Update("last_login", now)

	pkg.Success(c, dto.LoginResponse{
		Token:    token,
		ExpireAt: expireAt,
	})
}

func (h *AuthHandler) Logout(c *gin.Context) {
	// JWT 无状态登出，客户端清除 token 即可
	pkg.Success(c, nil)
}

func (h *AuthHandler) Profile(c *gin.Context) {
	userID, _ := c.Get(middleware.ContextUserIDKey)

	var user model.User
	if err := h.db.First(&user, userID).Error; err != nil {
		pkg.Fail(c, pkg.ErrCodeNotFound, "用户不存在")
		return
	}

	pkg.Success(c, dto.ProfileResponse{
		ID:       user.ID,
		Username: user.Username,
		Nickname: user.Nickname,
		Email:    user.Email,
		Role:     user.Role,
	})
}

// GetIDParam 从路由参数获取 int64 ID
func GetIDParam(c *gin.Context) (int64, error) {
	idStr := c.Param("id")
	return strconv.ParseInt(idStr, 10, 64)
}

// BindQueryInt 从查询参数获取 int
func BindQueryInt(c *gin.Context, key string, defaultVal int64) int64 {
	val, err := strconv.ParseInt(c.Query(key), 10, 64)
	if err != nil {
		return defaultVal
	}
	return val
}

// HealthCheck 健康检查
func HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"service": "go-server",
		"time":    time.Now().Format(time.RFC3339),
	})
}
