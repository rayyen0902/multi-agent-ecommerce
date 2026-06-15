package model

import (
	"time"

	"gorm.io/gorm"
)

// User 用户表
type User struct {
	ID        int64          `json:"id" gorm:"primaryKey;autoIncrement"`
	Username  string         `json:"username" gorm:"type:varchar(50);uniqueIndex;not null"`
	Password  string         `json:"-" gorm:"type:varchar(255);not null"`
	Nickname  string         `json:"nickname" gorm:"type:varchar(50)"`
	Email     string         `json:"email" gorm:"type:varchar(100)"`
	Role      string         `json:"role" gorm:"type:varchar(20);default:admin"`
	Status    int8           `json:"status" gorm:"default:1;comment:1=正常 0=禁用"`
	LastLogin *time.Time     `json:"last_login"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `json:"-" gorm:"index"`
}

func (User) TableName() string {
	return "users"
}
