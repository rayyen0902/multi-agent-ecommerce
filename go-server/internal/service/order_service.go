package service

import (
	"errors"
	"fmt"
	"time"

	"gorm.io/gorm"

	"github.com/multi-agent-ecom/go-server/internal/dto"
	"github.com/multi-agent-ecom/go-server/internal/model"
	"github.com/multi-agent-ecom/go-server/internal/repository"
)

type OrderService struct {
	orderRepo     *repository.OrderRepository
	productRepo   *repository.ProductRepository
	logisticsRepo *repository.LogisticsRepository
}

func NewOrderService(
	orderRepo *repository.OrderRepository,
	productRepo *repository.ProductRepository,
	logisticsRepo *repository.LogisticsRepository,
) *OrderService {
	return &OrderService{
		orderRepo:     orderRepo,
		productRepo:   productRepo,
		logisticsRepo: logisticsRepo,
	}
}

func (s *OrderService) List(query dto.OrderListQuery, page, pageSize int) ([]model.Order, int64, error) {
	filter := repository.OrderListFilter{
		Status:   query.Status,
		Platform: query.Platform,
		ShopID:   query.ShopID,
		Keyword:  query.Keyword,
		Sort:     query.Sort,
		Order:    query.Order,
	}

	if query.DateFrom != "" {
		t, err := time.Parse("2006-01-02", query.DateFrom)
		if err == nil {
			filter.DateFrom = t
		}
	}
	if query.DateTo != "" {
		t, err := time.Parse("2006-01-02", query.DateTo)
		if err == nil {
			filter.DateTo = t.AddDate(0, 0, 1) // 包含当天
		}
	}

	offset := (page - 1) * pageSize
	return s.orderRepo.List(filter, offset, pageSize)
}

func (s *OrderService) GetByID(id int64) (*model.Order, error) {
	return s.orderRepo.GetByID(id)
}

func (s *OrderService) GetByPlatformOrderNo(platformOrderNo string) (*model.Order, error) {
	return s.orderRepo.GetByPlatformOrderNo(platformOrderNo)
}

func (s *OrderService) UpdateRemark(id int64, remark string) error {
	_, err := s.orderRepo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return fmt.Errorf("订单不存在")
		}
		return err
	}
	return s.orderRepo.UpdateRemark(id, remark)
}

func (s *OrderService) UpdateTags(id int64, tags []string) error {
	return s.orderRepo.UpdateTags(id, tags)
}

func (s *OrderService) ShipOrder(id int64, shippingCompany, trackingNo string) error {
	order, err := s.orderRepo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return fmt.Errorf("订单不存在")
		}
		return err
	}

	if order.Status != model.OrderStatusPaid {
		return fmt.Errorf("当前订单状态 %s 不允许发货，仅待发货状态可发货", order.Status)
	}

	now := time.Now()
	// 更新订单状态
	if err := s.orderRepo.UpdateShipped(id, now); err != nil {
		return err
	}

	// 创建物流记录
	logistics := &model.Logistics{
		OrderID:         id,
		ShippingCompany: shippingCompany,
		TrackingNo:      trackingNo,
		Status:          model.LogisticsStatusInTransit,
		ShippedAt:       &now,
	}
	return s.logisticsRepo.Create(logistics)
}

func (s *OrderService) BatchShip(items []dto.BatchShipItem) ([]string, error) {
	var errs []string
	for _, item := range items {
		if err := s.ShipOrder(item.OrderID, item.ShippingCompany, item.TrackingNo); err != nil {
			errs = append(errs, fmt.Sprintf("订单ID %d: %s", item.OrderID, err.Error()))
		}
	}
	return errs, nil
}

func (s *OrderService) GetStatsOverview() (*dto.OrderStatsOverview, error) {
	todayStart, todayEnd := dto.TodayDateRange()

	todayCount, _ := s.orderRepo.CountByDateRange(todayStart, todayEnd)
	todaySales, _ := s.orderRepo.SumPayAmountByDateRange(todayStart, todayEnd)
	pendingShip, _ := s.orderRepo.CountByStatus(model.OrderStatusPaid)
	stockAlerts, _ := s.productRepo.CountStockAlerts()

	return &dto.OrderStatsOverview{
		TodayOrderCount:  todayCount,
		TodaySalesAmount: todaySales,
		PendingShipCount: pendingShip,
		StockAlertCount:  stockAlerts,
	}, nil
}

func (s *OrderService) CreateOrder(order *model.Order) error {
	// 生成系统订单号
	order.OrderNo = generateOrderNo()
	return s.orderRepo.CreateWithItems(order)
}

func generateOrderNo() string {
	return fmt.Sprintf("EOH%s%d", time.Now().Format("20060102150405"), time.Now().UnixNano()%10000)
}
