package model

import (
	"time"

	"gorm.io/gorm"
)

// Product 商品表
type Product struct {
	ID                    int64          `json:"id" gorm:"primaryKey;autoIncrement"`
	ShopID                int64          `json:"shop_id" gorm:"index;not null"`
	PlatformProductID     string         `json:"platform_product_id" gorm:"type:varchar(100)"`
	PlatformSkuID         string         `json:"platform_sku_id" gorm:"type:varchar(100)"`
	Name                  string         `json:"name" gorm:"type:varchar(255)"`
	SkuName               string         `json:"sku_name" gorm:"type:varchar(255)"`
	Price                 float64        `json:"price" gorm:"type:decimal(10,2)"`
	CostPrice             float64        `json:"cost_price" gorm:"type:decimal(10,2)"`
	Stock                 int            `json:"stock" gorm:"default:0"`
	StockWarningThreshold int            `json:"stock_warning_threshold" gorm:"default:10"`
	ImageURL              string         `json:"image_url" gorm:"type:varchar(500)"`
	Status                int8           `json:"status" gorm:"default:1;comment:1=在售 0=下架"`
	CreatedAt             time.Time      `json:"created_at"`
	UpdatedAt             time.Time      `json:"updated_at"`
	DeletedAt             gorm.DeletedAt `json:"-" gorm:"index"`

	Shop *Shop `json:"shop,omitempty" gorm:"foreignKey:ShopID"`
}

func (Product) TableName() string {
	return "products"
}
