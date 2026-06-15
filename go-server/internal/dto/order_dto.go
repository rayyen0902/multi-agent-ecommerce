package dto

import "time"

// OrderListQuery 订单列表查询参数
type OrderListQuery struct {
	Status   string  `form:"status"`
	Platform string  `form:"platform"`
	ShopID   int64   `form:"shop_id"`
	Keyword  string  `form:"keyword"`
	DateFrom string  `form:"date_from"`
	DateTo   string  `form:"date_to"`
	Sort     string  `form:"sort"`
	Order    string  `form:"order"`
}

// ShipRequest 发货请求
type ShipRequest struct {
	ShippingCompany string `json:"shipping_company" binding:"required"`
	TrackingNo      string `json:"tracking_no" binding:"required"`
}

// BatchShipItem 批量发货单项
type BatchShipItem struct {
	OrderID         int64  `json:"order_id" binding:"required"`
	ShippingCompany string `json:"shipping_company" binding:"required"`
	TrackingNo      string `json:"tracking_no" binding:"required"`
}

// BatchShipRequest 批量发货请求
type BatchShipRequest struct {
	Items []BatchShipItem `json:"items" binding:"required,min=1"`
}

// UpdateRemarkRequest 更新备注请求
type UpdateRemarkRequest struct {
	SellerRemark string `json:"seller_remark"`
}

// UpdateTagsRequest 更新标签请求
type UpdateTagsRequest struct {
	Tags []string `json:"tags"`
}

// OrderStatsOverview 订单统计概览
type OrderStatsOverview struct {
	TodayOrderCount   int64   `json:"today_order_count"`
	TodaySalesAmount  float64 `json:"today_sales_amount"`
	PendingShipCount  int64   `json:"pending_ship_count"`
	StockAlertCount   int64   `json:"stock_alert_count"`
}

// DashboardOverview 看板总览
type DashboardOverview struct {
	TodayOrderCount   int64   `json:"today_order_count"`
	TodaySalesAmount  float64 `json:"today_sales_amount"`
	PendingShipCount  int64   `json:"pending_ship_count"`
	StockAlertCount   int64   `json:"stock_alert_count"`
	YesterdayOrderCount  int64   `json:"yesterday_order_count"`
	YesterdaySalesAmount float64 `json:"yesterday_sales_amount"`
}

// SalesTrendPoint 销售趋势数据点
type SalesTrendPoint struct {
	Date       string  `json:"date"`
	OrderCount int64   `json:"order_count"`
	SalesAmount float64 `json:"sales_amount"`
}

// PlatformStat 平台统计
type PlatformStat struct {
	Platform    string  `json:"platform"`
	OrderCount  int64   `json:"order_count"`
	SalesAmount float64 `json:"sales_amount"`
}

// ShopRanking 店铺排行
type ShopRanking struct {
	ShopID      int64   `json:"shop_id"`
	ShopName    string  `json:"shop_name"`
	Platform    string  `json:"platform"`
	OrderCount  int64   `json:"order_count"`
	SalesAmount float64 `json:"sales_amount"`
}

// OrderStatusDistribution 订单状态分布
type OrderStatusDistribution struct {
	Status string `json:"status"`
	Count  int64  `json:"count"`
}

// ExportQuery 导出查询
type ExportQuery struct {
	Status   string `form:"status"`
	Platform string `form:"platform"`
	ShopID   int64  `form:"shop_id"`
	DateFrom string `form:"date_from"`
	DateTo   string `form:"date_to"`
}

// SyncTriggerRequest 触发同步请求(调用Python服务)
type SyncTriggerRequest struct {
	ShopID int64  `json:"shop_id"`
	Type   string `json:"type"` // orders / logistics
}

// SyncTriggerResponse 同步触发响应
type SyncTriggerResponse struct {
	TaskID string `json:"task_id"`
	Status string `json:"status"`
}

// SalesTrendQuery 销售趋势查询
type SalesTrendQuery struct {
	Period   string `form:"period"`   // daily / weekly / monthly
	DateFrom string `form:"date_from"`
	DateTo   string `form:"date_to"`
	Platform string `form:"platform"`
}

// LogisticsTrace 物流轨迹
type LogisticsTrace struct {
	Time     string `json:"time"`
	Info     string `json:"info"`
	Location string `json:"location"`
}

// ShippingCompany 快递公司
type ShippingCompany struct {
	Code string `json:"code"`
	Name string `json:"name"`
}

// CreateShopRequest 创建店铺请求
type CreateShopRequest struct {
	Name               string `json:"name" binding:"required"`
	Platform           string `json:"platform" binding:"required,oneof=taobao jd pdd"`
	PlatformShopID     string `json:"platform_shop_id"`
	AppKey             string `json:"app_key"`
	AppSecret          string `json:"app_secret"`
	SyncEnabled        bool   `json:"sync_enabled"`
	SyncIntervalMinutes int   `json:"sync_interval_minutes"`
}

// UpdateShopRequest 更新店铺请求
type UpdateShopRequest struct {
	Name               string `json:"name"`
	Status             *int8  `json:"status"`
	SyncEnabled        *bool  `json:"sync_enabled"`
	SyncIntervalMinutes *int  `json:"sync_interval_minutes"`
}

// CreateRuleRequest 创建规则请求
type CreateRuleRequest struct {
	Name       string `json:"name" binding:"required"`
	Type       string `json:"type" binding:"required"`
	ShopID     *int64 `json:"shop_id"`
	Platform   *string `json:"platform"`
	Conditions string `json:"conditions" binding:"required"`
	Actions    string `json:"actions" binding:"required"`
	Priority   int    `json:"priority"`
	Enabled    bool   `json:"enabled"`
}

// UpdateRuleRequest 更新规则请求
type UpdateRuleRequest struct {
	Name       string  `json:"name"`
	ShopID     *int64  `json:"shop_id"`
	Platform   *string `json:"platform"`
	Conditions string  `json:"conditions"`
	Actions    string  `json:"actions"`
	Priority   *int    `json:"priority"`
	Enabled    *bool   `json:"enabled"`
}

// TodayDateRange 返回今天的起止时间
func TodayDateRange() (time.Time, time.Time) {
	now := time.Now()
	start := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())
	end := start.AddDate(0, 0, 1)
	return start, end
}
