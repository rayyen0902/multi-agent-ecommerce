import { useEffect, useState } from 'react'
import { Card, Col, Row, Statistic, Spin, message } from 'antd'
import {
  ShoppingCartOutlined,
  DollarOutlined,
  SendOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import { dashboardApi } from '../../services/api'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'

const COLORS = ['#1890ff', '#52c41a', '#faad14', '#f5222d']

export default function Dashboard() {
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null)
  const [trend, setTrend] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const [ovRes, trRes] = await Promise.all([
          dashboardApi.overview(),
          dashboardApi.salesTrend(),
        ])
        setOverview(ovRes.data)
        setTrend(trRes.data || [])
      } catch (e) {
        console.error('Failed to fetch dashboard data:', e)
        message.error('数据看板加载失败，请稍后重试')
      }
      setLoading(false)
    }
    fetch()
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日订单" prefix={<ShoppingCartOutlined />}
              value={overview?.today_order_count || 0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日销售额" prefix={<DollarOutlined />}
              value={overview?.today_sales_amount || 0}
              precision={2} suffix="元"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待发货" prefix={<SendOutlined />}
              value={overview?.pending_ship_count || 0}
              valueStyle={{ color: (overview?.pending_ship_count || 0) > 0 ? '#cf1322' : undefined }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="库存预警" prefix={<WarningOutlined />}
              value={overview?.stock_alert_count || 0}
              valueStyle={{ color: (overview?.stock_alert_count || 0) > 0 ? '#faad14' : undefined }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="销售趋势（近30天）" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" fontSize={12} />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Line yAxisId="left" type="monotone" dataKey="order_count"
              stroke="#1890ff" name="订单数" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="sales_amount"
              stroke="#52c41a" name="销售额" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </div>
  )
}
