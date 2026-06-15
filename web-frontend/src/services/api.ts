import request from './request'
import type {
  PageResponse,
  Order,
  Shop,
  Product,
  LogisticsInfo,
  Rule,
  OrderFilter,
  CreateShopRequest,
  UpdateShopRequest,
  DashboardOverview,
  SalesTrendPoint,
  PlatformStat,
  ShopRankItem,
  OrderStatusDist,
} from '../types'

// 认证
export const authApi = {
  login: (username: string, password: string) =>
    request.post<{ token: string; expire_at: number }>('/auth/login', { username, password }),
  logout: () => request.post('/auth/logout'),
  profile: () => request.get('/auth/profile'),
}

// 订单
export const orderApi = {
  list: (params: OrderFilter) =>
    request.get<PageResponse<Order>>('/orders', { params }),
  detail: (id: number) => request.get<Order>(`/orders/${id}`),
  updateRemark: (id: number, seller_remark: string) =>
    request.put(`/orders/${id}/remark`, { seller_remark }),
  updateTags: (id: number, tags: string[]) =>
    request.put(`/orders/${id}/tags`, { tags }),
  ship: (id: number, data: { shipping_company: string; tracking_no: string }) =>
    request.post(`/orders/${id}/ship`, data),
  batchShip: (items: { id: number; shipping_company: string; tracking_no: string }[]) =>
    request.post('/orders/batch-ship', { items }),
  statsOverview: () => request.get<DashboardOverview>('/orders/stats/overview'),
}

// 店铺
export const shopApi = {
  list: (params?: Record<string, unknown>) =>
    request.get<PageResponse<Shop>>('/shops', { params }),
  detail: (id: number) => request.get<Shop>(`/shops/${id}`),
  create: (data: CreateShopRequest) => request.post<Shop>('/shops', data),
  update: (id: number, data: UpdateShopRequest) => request.put<Shop>(`/shops/${id}`, data),
  delete: (id: number) => request.post<void>(`/shops/${id}`),
  triggerSync: (id: number) => request.post(`/shops/${id}/sync`),
}

// 商品
export const productApi = {
  list: (params?: Record<string, unknown>) =>
    request.get<PageResponse<Product>>('/products', { params }),
  stockAlerts: (params?: Record<string, unknown>) =>
    request.get<PageResponse<Product>>('/products/stock-alerts', { params }),
}

// 物流
export const logisticsApi = {
  list: (params?: Record<string, unknown>) =>
    request.get<PageResponse<LogisticsInfo>>('/logistics', { params }),
  byOrder: (orderId: number) =>
    request.get<LogisticsInfo>(`/logistics/by-order/${orderId}`),
}

// 规则
export const ruleApi = {
  list: (params?: Record<string, unknown>) =>
    request.get<PageResponse<Rule>>('/rules', { params }),
}

// 看板
export const dashboardApi = {
  overview: () => request.get<DashboardOverview>('/dashboard/overview'),
  salesTrend: (params?: Record<string, unknown>) =>
    request.get<SalesTrendPoint[]>('/dashboard/sales-trend', { params }),
  platformStats: () => request.get<PlatformStat[]>('/dashboard/platform-stats'),
  shopRanking: () => request.get<ShopRankItem[]>('/dashboard/shop-ranking'),
  orderStatusDistribution: () =>
    request.get<OrderStatusDist[]>('/dashboard/order-status-distribution'),
}
