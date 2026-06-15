package service

import (
	"time"

	"github.com/multi-agent-ecom/go-server/internal/dto"
	"github.com/multi-agent-ecom/go-server/internal/repository"
)

type DashboardService struct {
	orderRepo   *repository.OrderRepository
	productRepo *repository.ProductRepository
}

func NewDashboardService(
	orderRepo *repository.OrderRepository,
	productRepo *repository.ProductRepository,
) *DashboardService {
	return &DashboardService{orderRepo: orderRepo, productRepo: productRepo}
}

func (s *DashboardService) GetOverview() (*dto.DashboardOverview, error) {
	todayStart, todayEnd := dto.TodayDateRange()
	yesterdayStart := todayStart.AddDate(0, 0, -1)
	yesterdayEnd := todayStart

	todayCount, _ := s.orderRepo.CountByDateRange(todayStart, todayEnd)
	todaySales, _ := s.orderRepo.SumPayAmountByDateRange(todayStart, todayEnd)
	yesterdayCount, _ := s.orderRepo.CountByDateRange(yesterdayStart, yesterdayEnd)
	yesterdaySales, _ := s.orderRepo.SumPayAmountByDateRange(yesterdayStart, yesterdayEnd)
	pendingShip, _ := s.orderRepo.CountByStatus("paid")
	stockAlerts, _ := s.productRepo.CountStockAlerts()

	return &dto.DashboardOverview{
		TodayOrderCount:      todayCount,
		TodaySalesAmount:     todaySales,
		PendingShipCount:     pendingShip,
		StockAlertCount:      stockAlerts,
		YesterdayOrderCount:  yesterdayCount,
		YesterdaySalesAmount: yesterdaySales,
	}, nil
}

func (s *DashboardService) GetSalesTrend(query dto.SalesTrendQuery) ([]dto.SalesTrendPoint, error) {
	// 默认最近30天
	dateFrom := time.Now().AddDate(0, 0, -30)
	dateTo := time.Now()

	if query.DateFrom != "" {
		if t, err := time.Parse("2006-01-02", query.DateFrom); err == nil {
			dateFrom = t
		}
	}
	if query.DateTo != "" {
		if t, err := time.Parse("2006-01-02", query.DateTo); err == nil {
			dateTo = t
		}
	}

	// 按日统计
	var points []dto.SalesTrendPoint
	for d := dateFrom; d.Before(dateTo.AddDate(0, 0, 1)); d = d.AddDate(0, 0, 1) {
		dayStart := time.Date(d.Year(), d.Month(), d.Day(), 0, 0, 0, 0, d.Location())
		dayEnd := dayStart.AddDate(0, 0, 1)

		count, _ := s.orderRepo.CountByDateRange(dayStart, dayEnd)
		sales, _ := s.orderRepo.SumPayAmountByDateRange(dayStart, dayEnd)

		points = append(points, dto.SalesTrendPoint{
			Date:        dayStart.Format("2006-01-02"),
			OrderCount:  count,
			SalesAmount: sales,
		})
	}

	return points, nil
}
