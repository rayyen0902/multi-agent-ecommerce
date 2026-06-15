package model

import (
	"time"

	"gorm.io/gorm"
)

// Shop 店铺表
type Shop struct {
	ID                 int64          `json:"id" gorm:"primaryKey;autoIncrement"`
	Name               string         `json:"name" gorm:"type:varchar(100);not null"`
	Platform           string         `json:"platform" gorm:"type:varchar(20);not null;comment:taobao/jd/pdd"`
	PlatformShopID     string         `json:"platform_shop_id" gorm:"type:varchar(100)"`
	AppKey             string         `json:"-" gorm:"type:varchar(100)"`
	AppSecret          string         `json:"-" gorm:"type:varchar(255)"`
	AccessToken        string         `json:"-" gorm:"type:text"`
	RefreshToken       string         `json:"-" gorm:"type:text"`
	TokenExpiresAt     *time.Time     `json:"token_expires_at"`
	Status             int8           `json:"status" gorm:"default:1;comment:1=正常 0=禁用 -1=过期"`
	SyncEnabled        bool           `json:"sync_enabled" gorm:"default:false"`
	SyncIntervalMinutes int           `json:"sync_interval_minutes" gorm:"default:15"`
	LastSyncAt         *time.Time     `json:"last_sync_at"`
	CreatedAt          time.Time      `json:"created_at"`
	UpdatedAt          time.Time      `json:"updated_at"`
	DeletedAt          gorm.DeletedAt `json:"-" gorm:"index"`
}

func (Shop) TableName() string {
	return "shops"
}
