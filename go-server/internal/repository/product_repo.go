package repository

import (
	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/model"
)

type ProductRepository struct {
	db *gorm.DB
}

func NewProductRepository(db *gorm.DB) *ProductRepository {
	return &ProductRepository{db: db}
}

func (r *ProductRepository) GetByID(id int64) (*model.Product, error) {
	var product model.Product
	err := r.db.Preload("Shop").First(&product, id).Error
	if err != nil {
		return nil, err
	}
	return &product, nil
}

func (r *ProductRepository) List(shopID int64, offset, limit int) ([]model.Product, int64, error) {
	var products []model.Product
	var total int64

	query := r.db.Model(&model.Product{})
	if shopID > 0 {
		query = query.Where("shop_id = ?", shopID)
	}

	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}
	err := query.Preload("Shop").Order("created_at DESC").Offset(offset).Limit(limit).Find(&products).Error
	return products, total, err
}

func (r *ProductRepository) Update(product *model.Product) error {
	return r.db.Save(product).Error
}

func (r *ProductRepository) UpdateStock(id int64, stock int) error {
	return r.db.Model(&model.Product{}).Where("id = ?", id).Update("stock", stock).Error
}

func (r *ProductRepository) GetStockAlerts(offset, limit int) ([]model.Product, int64, error) {
	var products []model.Product
	var total int64

	query := r.db.Model(&model.Product{}).
		Where("stock <= stock_warning_threshold AND status = 1")

	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}
	err := query.Preload("Shop").Order("stock ASC").Offset(offset).Limit(limit).Find(&products).Error
	return products, total, err
}

func (r *ProductRepository) CountStockAlerts() (int64, error) {
	var count int64
	err := r.db.Model(&model.Product{}).
		Where("stock <= stock_warning_threshold AND status = 1").
		Count(&count).Error
	return count, err
}
