package handler

import (
	"errors"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/dto"
	"github.com/multi-agent-ecom/go-server/internal/model"
	"github.com/multi-agent-ecom/go-server/internal/pkg"
	"github.com/multi-agent-ecom/go-server/internal/repository"
)

type ShopHandler struct {
	shopRepo *repository.ShopRepository
}

func NewShopHandler(shopRepo *repository.ShopRepository) *ShopHandler {
	return &ShopHandler{shopRepo: shopRepo}
}

func (h *ShopHandler) List(c *gin.Context) {
	pg := pkg.GetPagination(c)
	shops, total, err := h.shopRepo.List(pg.Offset, pg.PageSize)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}
	pkg.SuccessPage(c, shops, total, pg.Page, pg.PageSize)
}

func (h *ShopHandler) GetByID(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}
	shop, err := h.shopRepo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			pkg.Fail(c, pkg.ErrCodeShopNotFound, pkg.GetErrMsg(pkg.ErrCodeShopNotFound))
			return
		}
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}
	pkg.Success(c, shop)
}

func (h *ShopHandler) Create(c *gin.Context) {
	var req dto.CreateShopRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	shop := &model.Shop{
		Name:                req.Name,
		Platform:            req.Platform,
		PlatformShopID:      req.PlatformShopID,
		AppKey:              req.AppKey,
		AppSecret:           req.AppSecret,
		SyncEnabled:         req.SyncEnabled,
		SyncIntervalMinutes: req.SyncIntervalMinutes,
		Status:              1,
	}

	if err := h.shopRepo.Create(shop); err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "创建失败")
		return
	}
	pkg.Success(c, shop)
}

func (h *ShopHandler) Update(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}

	shop, err := h.shopRepo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			pkg.Fail(c, pkg.ErrCodeShopNotFound, pkg.GetErrMsg(pkg.ErrCodeShopNotFound))
			return
		}
		pkg.Fail(c, pkg.ErrCodeServerInternal, "查询失败")
		return
	}

	var req dto.UpdateShopRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "参数错误")
		return
	}

	if req.Name != "" {
		shop.Name = req.Name
	}
	if req.Status != nil {
		shop.Status = *req.Status
	}
	if req.SyncEnabled != nil {
		shop.SyncEnabled = *req.SyncEnabled
	}
	if req.SyncIntervalMinutes != nil {
		shop.SyncIntervalMinutes = *req.SyncIntervalMinutes
	}

	if err := h.shopRepo.Update(shop); err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "更新失败")
		return
	}
	pkg.Success(c, shop)
}

func (h *ShopHandler) Delete(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}
	if err := h.shopRepo.Delete(id); err != nil {
		pkg.Fail(c, pkg.ErrCodeServerInternal, "删除失败")
		return
	}
	pkg.Success(c, nil)
}

func (h *ShopHandler) TriggerSync(c *gin.Context) {
	id, err := GetIDParam(c)
	if err != nil {
		pkg.Fail(c, pkg.ErrCodeParamInvalid, "无效的ID")
		return
	}

	// 验证店铺存在
	if _, err := h.shopRepo.GetByID(id); err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			pkg.Fail(c, pkg.ErrCodeShopNotFound, pkg.GetErrMsg(pkg.ErrCodeShopNotFound))
			return
		}
	}

	// TODO: 调用 Python Worker 触发同步
	pkg.Success(c, gin.H{"status": "triggered", "shop_id": id})
}
