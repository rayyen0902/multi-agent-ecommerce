/** 通用 API 响应 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 分页响应 */
export interface PageResponse<T> {
  list: T[]
  total: number
  page: number
  page_size: number
}

/** 用户 */
export interface User {
  id: number
  username: string
  nickname: string
  email: string
  role: string
  shop_id: number | null
  status: number
  last_login: string | null
  created_at: string
  updated_at: string
}

/** 店铺 */
export interface Shop {
  id: number
  name: string
  platform: string
  platform_shop_id: string
  status: number
  sync_enabled: boolean
  sync_interval_minutes: number
  last_sync_at: string | null
  created_at: string
  updated_at: string
}

/** 订单 */
export interface Order {
  id: number
  order_no: string
  platform_order_no: string
  shop_id: number
  platform: string
  status: string
  buyer_name: string
  buyer_message: string
  seller_remark: string
  receiver_name: string
  receiver_phone: string
  receiver_province: string
  receiver_city: string
  receiver_district: string
  receiver_address: string
  total_amount: number
  discount_amount: number
  shipping_fee: number
  pay_amount: number
  payment_method: string
  platform_created_at: string | null
  platform_paid_at: string | null
  shipped_at: string | null
  completed_at: string | null
  synced_at: string | null
  tags: string[]
  items: OrderItem[]
  logistics: LogisticsInfo | null
  created_at: string
  updated_at: string
}

/** 订单项 */
export interface OrderItem {
  id: number
  order_id: number
  platform_item_id: string
  product_name: string
  sku_name: string
  price: number
  quantity: number
  total_price: number
  image_url: string
}

/** 物流 */
export interface LogisticsInfo {
  id: number
  order_id: number
  shipping_company: string
  shipping_company_code: string
  tracking_no: string
  status: string
  latest_info: string
  shipped_at: string | null
  delivered_at: string | null
  created_at: string
  updated_at: string
}

/** 商品 */
export interface Product {
  id: number
  shop_id: number
  platform_product_id: string
  platform_sku_id: string
  name: string
  sku_name: string
  price: number
  cost_price: number
  stock: number
  stock_warning_threshold: number
  image_url: string
  status: number
  created_at: string
  updated_at: string
}

/** 规则 */
export interface Rule {
  id: number
  name: string
  type: string
  shop_id: number | null
  platform: string | null
  conditions: Record<string, unknown> | null
  actions: Record<string, unknown> | null
  priority: number
  enabled: boolean
  trigger_count: number
  last_triggered_at: string | null
  created_at: string
  updated_at: string
}

/** 仪表盘概览 */
export interface DashboardOverview {
  total_orders: number
  total_amount: number
  pending_orders: number
  paid_orders: number
  shipped_orders: number
  completed_orders: number
  today_orders: number
  today_amount: number
}

/** 销售趋势 */
export interface SalesTrendPoint {
  date: string
  orders: number
  amount: number
}

/** 平台统计 */
export interface PlatformStat {
  platform: string
  orders: number
  amount: number
}

/** 店铺排行 */
export interface ShopRankItem {
  shop_id: number
  shop_name: string
  orders: number
  amount: number
}

/** 订单状态分布 */
export interface OrderStatusDist {
  status: string
  count: number
}

/** 分页查询参数 */
export interface PaginationParams {
  page?: number
  page_size?: number
}

/** 订单列表筛选 */
export interface OrderFilter extends PaginationParams {
  status?: string
  platform?: string
  shop_id?: number
  keyword?: string
  date_from?: string
  date_to?: string
  sort?: string
  order?: 'asc' | 'desc'
}

/** 创建店铺请求 */
export interface CreateShopRequest {
  name: string
  platform: string
  platform_shop_id?: string
  app_key: string
  app_secret: string
  sync_enabled?: boolean
  sync_interval_minutes?: number
}

/** 更新店铺请求 */
export interface UpdateShopRequest {
  name?: string
  status?: number
  sync_enabled?: boolean
  sync_interval_minutes?: number
}
