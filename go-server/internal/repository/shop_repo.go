package repository

import (
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/model"
)

type ShopRepository struct {
	db *gorm.DB
}

func NewShopRepository(db *gorm.DB) *ShopRepository {
	return &ShopRepository{db: db}
}

func (r *ShopRepository) Create(shop *model.Shop) error {
	return r.db.Create(shop).Error
}

func (r *ShopRepository) GetByID(id int64) (*model.Shop, error) {
	var shop model.Shop
	err := r.db.First(&shop, id).Error
	if err != nil {
		return nil, err
	}
	return &shop, nil
}

func (r *ShopRepository) List(offset, limit int) ([]model.Shop, int64, error) {
	var shops []model.Shop
	var total int64

	if err := r.db.Model(&model.Shop{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	err := r.db.Order("created_at DESC").Offset(offset).Limit(limit).Find(&shops).Error
	return shops, total, err
}

func (r *ShopRepository) Update(shop *model.Shop) error {
	return r.db.Save(shop).Error
}

func (r *ShopRepository) Delete(id int64) error {
	return r.db.Delete(&model.Shop{}, id).Error
}

func (r *ShopRepository) ListEnabled() ([]model.Shop, error) {
	var shops []model.Shop
	err := r.db.Where("status = 1 AND sync_enabled = true").Find(&shops).Error
	return shops, err
}

func (r *ShopRepository) UpdateToken(id int64, accessToken, refreshToken string, expiresAt interface{}) error {
	return r.db.Model(&model.Shop{}).Where("id = ?", id).
		Updates(map[string]interface{}{
			"access_token":    accessToken,
			"refresh_token":   refreshToken,
			"token_expires_at": expiresAt,
			"status":          1,
		}).Error
}

func (r *ShopRepository) UpdateLastSync(id int64) error {
	return r.db.Model(&model.Shop{}).Where("id = ?", id).
		Update("last_sync_at", gorm.Expr("NOW()")).Error
}
