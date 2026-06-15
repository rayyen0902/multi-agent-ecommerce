package repository

import (
	"time"

	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/model"
)

type RuleRepository struct {
	db *gorm.DB
}

func NewRuleRepository(db *gorm.DB) *RuleRepository {
	return &RuleRepository{db: db}
}

func (r *RuleRepository) Create(rule *model.Rule) error {
	return r.db.Create(rule).Error
}

func (r *RuleRepository) GetByID(id int64) (*model.Rule, error) {
	var rule model.Rule
	err := r.db.First(&rule, id).Error
	if err != nil {
		return nil, err
	}
	return &rule, nil
}

func (r *RuleRepository) List(offset, limit int) ([]model.Rule, int64, error) {
	var rules []model.Rule
	var total int64

	if err := r.db.Model(&model.Rule{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	err := r.db.Order("priority ASC, created_at DESC").Offset(offset).Limit(limit).Find(&rules).Error
	return rules, total, err
}

func (r *RuleRepository) Update(rule *model.Rule) error {
	return r.db.Save(rule).Error
}

func (r *RuleRepository) Delete(id int64) error {
	return r.db.Delete(&model.Rule{}, id).Error
}

func (r *RuleRepository) Toggle(id int64, enabled bool) error {
	return r.db.Model(&model.Rule{}).Where("id = ?", id).Update("enabled", enabled).Error
}

func (r *RuleRepository) ListEnabled() ([]model.Rule, error) {
	var rules []model.Rule
	err := r.db.Where("enabled = true").Order("priority ASC").Find(&rules).Error
	return rules, err
}

func (r *RuleRepository) UpdateTriggered(id int64) error {
	return r.db.Model(&model.Rule{}).Where("id = ?", id).
		Updates(map[string]interface{}{
			"last_triggered_at": time.Now(),
			"trigger_count":     gorm.Expr("trigger_count + 1"),
		}).Error
}

func (r *RuleRepository) GetLogs(ruleID int64, offset, limit int) ([]model.AutomationLog, int64, error) {
	var logs []model.AutomationLog
	var total int64

	query := r.db.Model(&model.AutomationLog{}).Where("rule_id = ?", ruleID)
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}
	err := query.Order("executed_at DESC").Offset(offset).Limit(limit).Find(&logs).Error
	return logs, total, err
}

func (r *RuleRepository) CreateLog(log *model.AutomationLog) error {
	return r.db.Create(log).Error
}
