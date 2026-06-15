package handler

import (
	"github.com/gin-gonic/gin"

	"github.com/multi-agent-ecom/go-server/internal/dto"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
	"github.com/multi-agent-ecom/go-server/internal/service"
)

type DashboardHandler struct {
	dashboardSvc *service.DashboardService
}

func NewDashboardHandler(dashboardSvc *service.DashboardService) *DashboardHandler {
	return &DashboardHandler{dashboardSvc: dashboardSvc}
}

func (h *DashboardHandler) Overview(c *gin.Context) {
	data, err := h.dashboardSvc.GetOverview()
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}
	pkg.Success(c, data)
}

func (h *DashboardHandler) SalesTrend(c *gin.Context) {
	var query dto.SalesTrendQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	data, err := h.dashboardSvc.GetSalesTrend(query)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}
	pkg.Success(c, data)
}

func (h *DashboardHandler) PlatformStats(c *gin.Context) {
	// TODO: 实现平台统计查询
	pkg.Success(c, []dto.PlatformStat{})
}

func (h *DashboardHandler) ShopRanking(c *gin.Context) {
	// TODO: 实现店铺排行查询
	pkg.Success(c, []dto.ShopRanking{})
}

func (h *DashboardHandler) OrderStatusDistribution(c *gin.Context) {
	// TODO: 实现订单状态分布查询
	pkg.Success(c, []dto.OrderStatusDistribution{})
}
