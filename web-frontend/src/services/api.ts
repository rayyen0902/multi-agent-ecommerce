import request from './request'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: number
}

export interface PageResponse<T> {
  list: T[]
  total: number
  page: number
  page_size: number
}

// 认证
export const authApi = {
  login: (username: string, password: string) =>
    request.post<ApiResponse<{ token: string; expire_at: number }>>('/auth/login', { username, password }),
  logout: () => request.post('/auth/logout'),
  profile: () => request.get('/auth/profile'),
}

// 订单
export const orderApi = {
  list: (params: Record<string, any>) =>
    request.get<ApiResponse<PageResponse<any>>>('/orders', { params }),
  detail: (id: number) => request.get<ApiResponse<any>>(`/orders/${id}`),
  updateRemark: (id: number, seller_remark: string) =>
    request.put(`/orders/${id}/remark`, { seller_remark }),
  updateTags: (id: number, tags: string[]) =>
    request.put(`/orders/${id}/tags`, { tags }),
  ship: (id: number, data: { shipping_company: string; tracking_no: string }) =>
    request.post(`/orders/${id}/ship`, data),
  batchShip: (items: any[]) => request.post('/orders/batch-ship', { items }),
  statsOverview: () => request.get('/orders/stats/overview'),
}

// 店铺
export const shopApi = {
  list: (params?: Record<string, any>) =>
    request.get<ApiResponse<PageResponse<any>>>('/shops', { params }),
  detail: (id: number) => request.get<ApiResponse<any>>(`/shops/${id}`),
  create: (data: any) => request.post('/shops', data),
  update: (id: number, data: any) => request.put(`/shops/${id}`, data),
  delete: (id: number) => request.delete(`/shops/${id}`),
  triggerSync: (id: number) => request.post(`/shops/${id}/sync`),
}

// 商品
export const productApi = {
  list: (params?: Record<string, any>) =>
    request.get<ApiResponse<PageResponse<any>>>('/products', { params }),
  stockAlerts: (params?: Record<string, any>) =>
    request.get<ApiResponse<PageResponse<any>>>('/products/stock-alerts', { params }),
}

// 物流
export const logisticsApi = {
  list: (params?: Record<string, any>) =>
    request.get<ApiResponse<PageResponse<any>>>('/logistics', { params }),
  byOrder: (orderId: number) =>
    request.get<ApiResponse<any>>(`/logistics/by-order/${orderId}`),
}

// 规则
export const ruleApi = {
  list: (params?: Record<string, any>) =>
    request.get<ApiResponse<PageResponse<any>>>('/rules', { params }),
}

// 看板
export const dashboardApi = {
  overview: () => request.get('/dashboard/overview'),
  salesTrend: (params?: Record<string, any>) =>
    request.get('/dashboard/sales-trend', { params }),
  platformStats: () => request.get('/dashboard/platform-stats'),
  shopRanking: () => request.get('/dashboard/shop-ranking'),
}
