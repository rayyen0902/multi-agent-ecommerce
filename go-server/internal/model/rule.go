package model

import (
	"time"

	"gorm.io/gorm"
)

// 规则类型常量
const (
	RuleTypeAutoShip    = "auto_ship"    // 自动发货
	RuleTypeAutoReview  = "auto_review"  // 自动评价
	RuleTypeStockAlert  = "stock_alert"  // 库存预警
	RuleTypeCustom      = "custom"       // 自定义
)

// Rule 自动化规则表
type Rule struct {
	ID             int64          `json:"id" gorm:"primaryKey;autoIncrement"`
	Name           string         `json:"name" gorm:"type:varchar(100);not null"`
	Type           string         `json:"type" gorm:"type:varchar(30);not null"`
	ShopID         *int64         `json:"shop_id" gorm:"index"`
	Platform       *string        `json:"platform" gorm:"type:varchar(20)"`
	Conditions     string         `json:"conditions" gorm:"type:jsonb;comment:触发条件"`
	Actions        string         `json:"actions" gorm:"type:jsonb;comment:执行动作"`
	Priority       int            `json:"priority" gorm:"default:100"`
	Enabled        bool           `json:"enabled" gorm:"default:false"`
	LastTriggeredAt *time.Time    `json:"last_triggered_at"`
	TriggerCount   int64          `json:"trigger_count" gorm:"default:0"`
	CreatedAt      time.Time      `json:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at"`
	DeletedAt      gorm.DeletedAt `json:"-" gorm:"index"`
}

func (Rule) TableName() string {
	return "rules"
}

// AutomationLog 自动化执行日志
type AutomationLog struct {
	ID           int64     `json:"id" gorm:"primaryKey;autoIncrement"`
	RuleID       int64     `json:"rule_id" gorm:"index;not null"`
	OrderID      *int64    `json:"order_id" gorm:"index"`
	ActionType   string    `json:"action_type" gorm:"type:varchar(30)"`
	Status       string    `json:"status" gorm:"type:varchar(20);comment:success/failed/skipped"`
	Detail       string    `json:"detail" gorm:"type:jsonb"`
	ErrorMessage string    `json:"error_message" gorm:"type:text"`
	ExecutedAt   time.Time `json:"executed_at"`
}

func (AutomationLog) TableName() string {
	return "automation_logs"
}
