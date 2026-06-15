package router

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/config"
	"github.com/multi-agent-ecom/go-server/internal/handler"
	"github.com/multi-agent-ecom/go-server/internal/middleware"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
	"github.com/multi-agent-ecom/go-server/internal/repository"
	"github.com/multi-agent-ecom/go-server/internal/service"
)

func Setup(cfg *config.Config, db *gorm.DB) *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(middleware.CorsMiddleware())
	r.Use(middleware.LoggerMiddleware())

	// 初始化仓储层
	orderRepo := repository.NewOrderRepository(db)
	shopRepo := repository.NewShopRepository(db)
	productRepo := repository.NewProductRepository(db)
	logisticsRepo := repository.NewLogisticsRepository(db)
	ruleRepo := repository.NewRuleRepository(db)

	// 初始化服务层
	orderSvc := service.NewOrderService(orderRepo, productRepo, logisticsRepo)
	dashboardSvc := service.NewDashboardService(orderRepo, productRepo)

	// 初始化 Handler 层
	authHandler := handler.NewAuthHandler(db, cfg.JWT.Secret, cfg.JWT.ExpireHour)
	orderHandler := handler.NewOrderHandler(orderSvc)
	shopHandler := handler.NewShopHandler(shopRepo)
	dashboardHandler := handler.NewDashboardHandler(dashboardSvc)

	// 健康检查
	r.GET("/health", handler.HealthCheck)

	// API v1
	v1 := r.Group("/api/v1")
	{
		// 认证（无需登录）
		auth := v1.Group("/auth")
		{
			auth.POST("/login", authHandler.Login)
		}

		// 需要登录的接口
		authorized := v1.Group("")
		authorized.Use(middleware.AuthMiddleware(cfg.JWT.Secret))
		{
			// 认证
			authorized.POST("/auth/logout", authHandler.Logout)
			authorized.GET("/auth/profile", authHandler.Profile)

			// 店铺管理
			shops := authorized.Group("/shops")
			{
				shops.GET("", shopHandler.List)
				shops.POST("", shopHandler.Create)
				shops.GET("/:id", shopHandler.GetByID)
				shops.PUT("/:id", shopHandler.Update)
				shops.DELETE("/:id", shopHandler.Delete)
				shops.POST("/:id/sync", shopHandler.TriggerSync)
			}

			// 订单管理
			orders := authorized.Group("/orders")
			{
				orders.GET("", orderHandler.List)
				orders.GET("/:id", orderHandler.GetByID)
				orders.GET("/by-platform/:platform_order_no", orderHandler.GetByPlatformOrderNo)
				orders.PUT("/:id/remark", orderHandler.UpdateRemark)
				orders.PUT("/:id/tags", orderHandler.UpdateTags)
				orders.POST("/:id/ship", orderHandler.Ship)
				orders.POST("/batch-ship", orderHandler.BatchShip)
				orders.GET("/stats/overview", orderHandler.StatsOverview)
			}

			// 数据看板
			dashboard := authorized.Group("/dashboard")
			{
				dashboard.GET("/overview", dashboardHandler.Overview)
				dashboard.GET("/sales-trend", dashboardHandler.SalesTrend)
				dashboard.GET("/platform-stats", dashboardHandler.PlatformStats)
				dashboard.GET("/shop-ranking", dashboardHandler.ShopRanking)
				dashboard.GET("/order-status-distribution", dashboardHandler.OrderStatusDistribution)
			}

			// 商品管理
			products := authorized.Group("/products")
			{
				products.GET("", func(c *gin.Context) {
					pg := pkg.GetPagination(c)
					shopID := handler.BindQueryInt(c, "shop_id", 0)
					list, total, err := productRepo.List(shopID, pg.Offset, pg.PageSize)
					if err != nil {
						pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
						return
					}
					pkg.SuccessPage(c, list, total, pg.Page, pg.PageSize)
				})
				products.GET("/stock-alerts", func(c *gin.Context) {
					pg := pkg.GetPagination(c)
					list, total, err := productRepo.GetStockAlerts(pg.Offset, pg.PageSize)
					if err != nil {
						pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
						return
					}
					pkg.SuccessPage(c, list, total, pg.Page, pg.PageSize)
				})
			}

			// 物流管理
			logistics := authorized.Group("/logistics")
			{
				logistics.GET("", func(c *gin.Context) {
					pg := pkg.GetPagination(c)
					list, total, err := logisticsRepo.List(pg.Offset, pg.PageSize)
					if err != nil {
						pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
						return
					}
					pkg.SuccessPage(c, list, total, pg.Page, pg.PageSize)
				})
				logistics.GET("/by-order/:order_id", func(c *gin.Context) {
					orderID, _ := handler.GetIDParam(c)
					logi, err := logisticsRepo.GetByOrderID(orderID)
					if err != nil {
						pkg.Fail(c, pkg.ErrCodeNotFound, "物流信息不存在")
						return
					}
					pkg.Success(c, logi)
				})
			}

			// 规则管理
			rules := authorized.Group("/rules")
			{
				rules.GET("", func(c *gin.Context) {
					pg := pkg.GetPagination(c)
					list, total, err := ruleRepo.List(pg.Offset, pg.PageSize)
					if err != nil {
						pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
						return
					}
					pkg.SuccessPage(c, list, total, pg.Page, pg.PageSize)
				})
			}
		}
	}

	return r
}
