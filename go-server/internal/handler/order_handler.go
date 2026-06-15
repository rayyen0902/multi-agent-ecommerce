package handler

import (
	"errors"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/dto"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
	"github.com/multi-agent-ecom/go-server/internal/service"
)

type OrderHandler struct {
	orderSvc *service.OrderService
}

func NewOrderHandler(orderSvc *service.OrderService) *OrderHandler {
	return &OrderHandler{orderSvc: orderSvc}
}

func (h *OrderHandler) List(c *gin.Context) {
	var query dto.OrderListQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	pg := pkg.GetPagination(c)
	orders, total, err := h.orderSvc.List(query, pg.Page, pg.PageSize)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}

	pkg.SuccessPage(c, orders, total, pg.Page, pg.PageSize)
}

func (h *OrderHandler) GetByID(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}

	order, err := h.orderSvc.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			pkg.Fail(c, pkg.ErrCodeOrderNotFound, pkg.GetErrMsg(pkg.ErrCodeOrderNotFound))
			return
		}
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}

	pkg.Success(c, order)
}

func (h *OrderHandler) GetByPlatformOrderNo(c *gin.Context) {
	platformOrderNo := c.Param("platform_order_no")
	order, err := h.orderSvc.GetByPlatformOrderNo(platformOrderNo)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			pkg.Fail(c, pkg.ErrCodeOrderNotFound, pkg.GetErrMsg(pkg.ErrCodeOrderNotFound))
			return
		}
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}
	pkg.Success(c, order)
}

func (h *OrderHandler) UpdateRemark(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}

	var req dto.UpdateRemarkRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	if err := h.orderSvc.UpdateRemark(id, req.SellerRemark); err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, err.Error())
		return
	}
	pkg.Success(c, nil)
}

func (h *OrderHandler) UpdateTags(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}

	var req dto.UpdateTagsRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	if err := h.orderSvc.UpdateTags(id, req.Tags); err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, err.Error())
		return
	}
	pkg.Success(c, nil)
}

func (h *OrderHandler) Ship(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}

	var req dto.ShipRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	if err := h.orderSvc.ShipOrder(id, req.ShippingCompany, req.TrackingNo); err != nil {
		pkg.Fail(c, pkg.ErrCodeOrderStatusErr, err.Error())
		return
	}
	pkg.Success(c, nil)
}

func (h *OrderHandler) BatchShip(c *gin.Context) {
	var req dto.BatchShipRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	errs, err := h.orderSvc.BatchShip(req.Items)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, err.Error())
		return
	}

	pkg.Success(c, gin.H{
		"total":   len(req.Items),
		"errors":  errs,
		"success": len(req.Items) - len(errs),
	})
}

func (h *OrderHandler) StatsOverview(c *gin.Context) {
	stats, err := h.orderSvc.GetStatsOverview()
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "统计查询失败")
		return
	}
	pkg.Success(c, stats)
}
