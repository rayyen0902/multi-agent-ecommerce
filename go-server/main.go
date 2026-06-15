package main

import (
	"fmt"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"github.com/multi-agent-ecom/go-server/config"
	"github.com/multi-agent-ecom/go-server/internal/model"
	"github.com/multi-agent-ecom/go-server/router"
)

func main() {
	// 加载配置
	cfg := config.Load()

	// 连接数据库
	db, err := gorm.Open(postgres.Open(cfg.Database.DSN()), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		log.Fatalf("数据库连接失败: %v", err)
	}

	// 自动迁移（开发环境使用，生产环境应使用 migration 脚本）
	if err := db.AutoMigrate(
		&model.User{},
		&model.Shop{},
		&model.Product{},
		&model.Order{},
		&model.OrderItem{},
		&model.Logistics{},
		&model.Rule{},
		&model.AutomationLog{},
	); err != nil {
		log.Fatalf("数据库迁移失败: %v", err)
	}

	// 设置路由
	r := router.Setup(cfg, db)

	// 启动服务
	addr := fmt.Sprintf(":%d", cfg.Server.Port)
	log.Printf("Go 服务启动在 %s", addr)
	if err := r.Run(addr); err != nil {
		log.Fatalf("服务启动失败: %v", err)
	}
}
