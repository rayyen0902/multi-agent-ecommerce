package middleware

import (
	"strconv"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/model"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
)

// ShopAuthMiddleware 检查当前用户是否有权访问指定店铺
// admin 角色可以访问所有店铺
// 普通用户只能访问其关联的店铺（User.ShopID == 店铺ID）
func ShopAuthMiddleware(db *gorm.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		role, exists := c.Get(ContextRoleKey)
		if !exists || role != "admin" {
			userID, _ := c.Get(ContextUserIDKey)
			userIDInt, ok := userID.(int64)
			if !ok || userIDInt <= 0 {
				pkg.FailWithStatus(c, 403, 403, "无权访问该店铺")
				c.Abort()
				return
			}

			shopIDStr := c.Param("id")
			if shopIDStr == "" {
				c.Next()
				return
			}

			shopID, err := strconv.ParseInt(shopIDStr, 10, 64)
			if err != nil || shopID <= 0 {
				c.Next()
				return
			}

			// 查询用户的 ShopID
			var user model.User
			if err := db.Select("shop_id").First(&user, userIDInt).Error; err != nil {
				pkg.FailWithStatus(c, 403, 403, "无权访问该店铺")
				c.Abort()
				return
			}

			// admin 用户的 ShopID 可以为空，普通用户必须匹配
			if user.ShopID == nil || *user.ShopID != shopID {
				pkg.FailWithStatus(c, 403, 403, "无权访问该店铺")
				c.Abort()
				return
			}
		}
		c.Next()
	}
}
