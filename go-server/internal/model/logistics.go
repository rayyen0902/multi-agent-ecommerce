package model

import (
	"time"

	"gorm.io/gorm"
)

// 物流状态常量
const (
	LogisticsStatusPending   = "pending"    // 待发货
	LogisticsStatusInTransit = "in_transit" // 运输中
	LogisticsStatusDelivered = "delivered"  // 已派送
	LogisticsStatusSigned    = "signed"     // 已签收
)

// Logistics 物流表
type Logistics struct {
	ID                  int64          `json:"id" gorm:"primaryKey;autoIncrement"`
	OrderID             int64          `json:"order_id" gorm:"uniqueIndex;not null"`
	ShippingCompany     string         `json:"shipping_company" gorm:"type:varchar(50)"`
	ShippingCompanyCode string         `json:"shipping_company_code" gorm:"type:varchar(20)"`
	TrackingNo          string         `json:"tracking_no" gorm:"type:varchar(100);index"`
	Status              string         `json:"status" gorm:"type:varchar(20);default:pending"`
	LatestInfo          string         `json:"latest_info" gorm:"type:text"`
	Traces              string         `json:"traces" gorm:"type:jsonb;comment:物流轨迹数组"`
	ShippedAt           *time.Time     `json:"shipped_at"`
	DeliveredAt         *time.Time     `json:"delivered_at"`
	LastTrackedAt       *time.Time     `json:"last_tracked_at"`
	CreatedAt           time.Time      `json:"created_at"`
	UpdatedAt           time.Time      `json:"updated_at"`
	DeletedAt           gorm.DeletedAt `json:"-" gorm:"index"`

	Order *Order `json:"order,omitempty" gorm:"foreignKey:OrderID"`
}

func (Logistics) TableName() string {
	return "logistics"
}
