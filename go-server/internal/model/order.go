package model

import (
	"time"

	"github.com/lib/pq"
	"gorm.io/gorm"
)

// 订单状态常量
const (
	OrderStatusPending   = "pending"   // 待付款
	OrderStatusPaid      = "paid"      // 待发货
	OrderStatusShipped   = "shipped"   // 已发货
	OrderStatusDelivered = "delivered" // 已签收
	OrderStatusCompleted = "completed" // 已完成
	OrderStatusClosed    = "closed"    // 已关闭
	OrderStatusRefunding = "refunding" // 退款中
)

// Order 订单主表
type Order struct {
	ID                int64          `json:"id" gorm:"primaryKey;autoIncrement"`
	OrderNo           string         `json:"order_no" gorm:"type:varchar(64);uniqueIndex;not null"`
	PlatformOrderNo   string         `json:"platform_order_no" gorm:"type:varchar(100);index"`
	ShopID            int64          `json:"shop_id" gorm:"index;not null"`
	Platform          string         `json:"platform" gorm:"type:varchar(20);not null"`
	Status            string         `json:"status" gorm:"type:varchar(20);index;not null;default:pending"`
	BuyerName         string         `json:"buyer_name" gorm:"type:varchar(100)"`
	BuyerMessage      string         `json:"buyer_message" gorm:"type:text"`
	SellerRemark      string         `json:"seller_remark" gorm:"type:text"`
	ReceiverName      string         `json:"receiver_name" gorm:"type:varchar(50)"`
	ReceiverPhone     string         `json:"receiver_phone" gorm:"type:varchar(255)"`
	ReceiverProvince  string         `json:"receiver_province" gorm:"type:varchar(20)"`
	ReceiverCity      string         `json:"receiver_city" gorm:"type:varchar(20)"`
	ReceiverDistrict  string         `json:"receiver_district" gorm:"type:varchar(20)"`
	ReceiverAddress   string         `json:"receiver_address" gorm:"type:varchar(512)"`
	TotalAmount       float64        `json:"total_amount" gorm:"type:decimal(10,2)"`
	DiscountAmount    float64        `json:"discount_amount" gorm:"type:decimal(10,2);default:0"`
	ShippingFee       float64        `json:"shipping_fee" gorm:"type:decimal(10,2);default:0"`
	PayAmount         float64        `json:"pay_amount" gorm:"type:decimal(10,2)"`
	PaymentMethod     string         `json:"payment_method" gorm:"type:varchar(20)"`
	PlatformCreatedAt *time.Time     `json:"platform_created_at" gorm:"index"`
	PlatformPaidAt    *time.Time     `json:"platform_paid_at"`
	ShippedAt         *time.Time     `json:"shipped_at"`
	CompletedAt       *time.Time     `json:"completed_at"`
	SyncedAt          *time.Time     `json:"synced_at"`
	RawData           string         `json:"-" gorm:"type:jsonb"`
	Tags              pq.StringArray `json:"tags" gorm:"type:varchar(255)[]"`
	CreatedAt         time.Time      `json:"created_at"`
	UpdatedAt         time.Time      `json:"updated_at"`
	DeletedAt         gorm.DeletedAt `json:"-" gorm:"index"`

	// 关联
	Shop      *Shop        `json:"shop,omitempty" gorm:"foreignKey:ShopID"`
	Items     []OrderItem  `json:"items,omitempty" gorm:"foreignKey:OrderID"`
	Logistics *Logistics   `json:"logistics,omitempty" gorm:"foreignKey:OrderID"`
}

func (Order) TableName() string {
	return "orders"
}

// OrderItem 订单明细表
type OrderItem struct {
	ID               int64   `json:"id" gorm:"primaryKey;autoIncrement"`
	OrderID          int64   `json:"order_id" gorm:"index;not null"`
	PlatformItemID   string  `json:"platform_item_id" gorm:"type:varchar(100)"`
	ProductID        *int64  `json:"product_id"`
	ProductName      string  `json:"product_name" gorm:"type:varchar(255)"`
	SkuName          string  `json:"sku_name" gorm:"type:varchar(255)"`
	Price            float64 `json:"price" gorm:"type:decimal(10,2)"`
	Quantity         int     `json:"quantity"`
	TotalPrice       float64 `json:"total_price" gorm:"type:decimal(10,2)"`
	ImageURL         string  `json:"image_url" gorm:"type:varchar(500)"`
}

func (OrderItem) TableName() string {
	return "order_items"
}
