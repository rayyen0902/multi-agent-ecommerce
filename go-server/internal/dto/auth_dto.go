package dto

// LoginRequest 登录请求
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// LoginResponse 登录响应
type LoginResponse struct {
	Token    string `json:"token"`
	ExpireAt int64  `json:"expire_at"`
}

// ProfileResponse 用户信息响应
type ProfileResponse struct {
	ID       int64  `json:"id"`
	Username string `json:"username"`
	Nickname string `json:"nickname"`
	Email    string `json:"email"`
	Role     string `json:"role"`
}
