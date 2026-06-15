package repository

import (
	"time"

	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/model"
)

type OrderRepository struct {
	db *gorm.DB
}

func NewOrderRepository(db *gorm.DB) *OrderRepository {
	return &OrderRepository{db: db}
}

func (r *OrderRepository) Create(order *model.Order) error {
	return r.db.Create(order).Error
}

func (r *OrderRepository) CreateWithItems(order *model.Order) error {
	return r.db.Create(order).Error // items will be created via association
}

func (r *OrderRepository) GetByID(id int64) (*model.Order, error) {
	var order model.Order
	err := r.db.Preload("Items").Preload("Logistics").Preload("Shop").
		First(&order, id).Error
	if err != nil {
		return nil, err
	}
	return &order, nil
}

func (r *OrderRepository) GetByPlatformOrderNo(platformOrderNo string) (*model.Order, error) {
	var order model.Order
	err := r.db.Preload("Items").Preload("Logistics").
		Where("platform_order_no = ?", platformOrderNo).First(&order).Error
	if err != nil {
		return nil, err
	}
	return &order, nil
}

type OrderListFilter struct {
	Status   string
	Platform string
	ShopID   int64
	Keyword  string
	DateFrom time.Time
	DateTo   time.Time
	Sort     string
	Order    string
}

func (r *OrderRepository) List(filter OrderListFilter, offset, limit int) ([]model.Order, int64, error) {
	var orders []model.Order
	var total int64

	query := r.db.Model(&model.Order{})

	if filter.Status != "" {
		query = query.Where("status IN (?)", splitComma(filter.Status))
	}
	if filter.Platform != "" {
		query = query.Where("platform = ?", filter.Platform)
	}
	if filter.ShopID > 0 {
		query = query.Where("shop_id = ?", filter.ShopID)
	}
	if filter.Keyword != "" {
		keyword := "%" + filter.Keyword + "%"
		query = query.Where("order_no LIKE ? OR platform_order_no LIKE ? OR buyer_name LIKE ? OR receiver_name LIKE ?",
			keyword, keyword, keyword, keyword)
	}
	if !filter.DateFrom.IsZero() {
		query = query.Where("platform_created_at >= ?", filter.DateFrom)
	}
	if !filter.DateTo.IsZero() {
		query = query.Where("platform_created_at <= ?", filter.DateTo)
	}

	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}

	allowedSortFields := map[string]bool{
		"platform_created_at": true,
		"status":            true,
		"pay_amount":        true,
		"updated_at":        true,
	}
	validSort := "platform_created_at"
	if allowedSortFields[filter.Sort] {
		validSort = filter.Sort
	}
	orderDir := "DESC"
	if filter.Order == "asc" {
		orderDir = "ASC"
	}

	err := query.Preload("Items").Preload("Shop").
		Order(validSort + " " + orderDir).
		Offset(offset).Limit(limit).
		Find(&orders).Error

	return orders, total, err
}

func (r *OrderRepository) UpdateStatus(id int64, status string) error {
	return r.db.Model(&model.Order{}).Where("id = ?", id).Update("status", status).Error
}

func (r *OrderRepository) UpdateRemark(id int64, remark string) error {
	return r.db.Model(&model.Order{}).Where("id = ?", id).Update("seller_remark", remark).Error
}

func (r *OrderRepository) UpdateTags(id int64, tags []string) error {
	return r.db.Model(&model.Order{}).Where("id = ?", id).Update("tags", tags).Error
}

func (r *OrderRepository) UpdateShipped(id int64, shippedAt time.Time) error {
	return r.db.Model(&model.Order{}).Where("id = ?", id).
		Updates(map[string]interface{}{
			"status":     model.OrderStatusShipped,
			"shipped_at": shippedAt,
		}).Error
}

func (r *OrderRepository) CountByStatus(status string) (int64, error) {
	var count int64
	err := r.db.Model(&model.Order{}).Where("status = ?", status).Count(&count).Error
	return count, err
}

func (r *OrderRepository) CountByDateRange(start, end time.Time) (int64, error) {
	var count int64
	err := r.db.Model(&model.Order{}).
		Where("platform_created_at >= ? AND platform_created_at < ?", start, end).
		Count(&count).Error
	return count, err
}

func (r *OrderRepository) SumPayAmountByDateRange(start, end time.Time) (float64, error) {
	var sum float64
	err := r.db.Model(&model.Order{}).
		Where("platform_created_at >= ? AND platform_created_at < ? AND status != ?",
			start, end, model.OrderStatusClosed).
		Select("COALESCE(SUM(pay_amount), 0)").
		Scan(&sum).Error
	return sum, err
}

func (r *OrderRepository) ExistsByPlatformOrderNo(platformOrderNo string) (bool, error) {
	var count int64
	err := r.db.Model(&model.Order{}).
		Where("platform_order_no = ?", platformOrderNo).
		Count(&count).Error
	return count > 0, err
}

func splitComma(s string) []string {
	var result []string
	current := ""
	for _, c := range s {
		if c == ',' {
			if current != "" {
				result = append(result, current)
			}
			current = ""
		} else {
			current += string(c)
		}
	}
	if current != "" {
		result = append(result, current)
	}
	return result
}
