package repository

import (
	"time"

	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/model"
)

type LogisticsRepository struct {
	db *gorm.DB
}

func NewLogisticsRepository(db *gorm.DB) *LogisticsRepository {
	return &LogisticsRepository{db: db}
}

func (r *LogisticsRepository) Create(logistics *model.Logistics) error {
	return r.db.Create(logistics).Error
}

func (r *LogisticsRepository) GetByID(id int64) (*model.Logistics, error) {
	var logistics model.Logistics
	err := r.db.Preload("Order").First(&logistics, id).Error
	if err != nil {
		return nil, err
	}
	return &logistics, nil
}

func (r *LogisticsRepository) GetByOrderID(orderID int64) (*model.Logistics, error) {
	var logistics model.Logistics
	err := r.db.Where("order_id = ?", orderID).First(&logistics).Error
	if err != nil {
		return nil, err
	}
	return &logistics, nil
}

func (r *LogisticsRepository) List(offset, limit int) ([]model.Logistics, int64, error) {
	var list []model.Logistics
	var total int64

	if err := r.db.Model(&model.Logistics{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	err := r.db.Preload("Order").Order("created_at DESC").Offset(offset).Limit(limit).Find(&list).Error
	return list, total, err
}

func (r *LogisticsRepository) UpdateTraces(id int64, traces string, status, latestInfo string) error {
	return r.db.Model(&model.Logistics{}).Where("id = ?", id).
		Updates(map[string]interface{}{
			"traces":        traces,
			"status":        status,
			"latest_info":   latestInfo,
			"last_tracked_at": time.Now(),
		}).Error
}

func (r *LogisticsRepository) UpdateDelivered(id int64) error {
	now := time.Now()
	return r.db.Model(&model.Logistics{}).Where("id = ?", id).
		Updates(map[string]interface{}{
			"status":       model.LogisticsStatusSigned,
			"delivered_at": now,
		}).Error
}

func (r *LogisticsRepository) ListPendingTrack(offset, limit int) ([]model.Logistics, error) {
	var list []model.Logistics
	err := r.db.Where("status IN (?, ?)",
		model.LogisticsStatusPending, model.LogisticsStatusInTransit).
		Order("last_tracked_at ASC NULLS FIRST").
		Offset(offset).Limit(limit).
		Find(&list).Error
	return list, err
}
