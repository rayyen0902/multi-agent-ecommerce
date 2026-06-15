import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Descriptions, Table, Tag, Button, Timeline, Spin, Empty, message } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { orderApi } from '../../services/api'
import type { Order } from '../../types'

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待付款' },
  paid: { color: 'orange', text: '待发货' },
  shipped: { color: 'blue', text: '已发货' },
  delivered: { color: 'cyan', text: '已签收' },
  completed: { color: 'green', text: '已完成' },
  closed: { color: 'red', text: '已关闭' },
}

export default function OrderDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await orderApi.detail(Number(id))
        setOrder(res.data)
      } catch (e) {
        console.error('Failed to fetch order:', e)
        message.error('订单详情加载失败，请稍后重试')
      }
      setLoading(false)
    }
    fetch()
  }, [id])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  if (!order) return <Empty description="订单不存在" />

  const itemColumns = [
    { title: '商品名', dataIndex: 'product_name' },
    { title: '规格', dataIndex: 'sku_name' },
    { title: '单价', dataIndex: 'price', render: (v: number) => `¥${v.toFixed(2)}` },
    { title: '数量', dataIndex: 'quantity' },
    { title: '小计', dataIndex: 'total_price', render: (v: number) => `¥${v.toFixed(2)}` },
  ]

  const s = statusMap[order.status] || { color: 'default', text: order.status }

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        返回
      </Button>

      <Card title={`订单详情 - ${order.order_no}`} extra={<Tag color={s.color}>{s.text}</Tag>}>
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="系统订单号">{order.order_no}</Descriptions.Item>
          <Descriptions.Item label="平台订单号">{order.platform_order_no}</Descriptions.Item>
          <Descriptions.Item label="平台">{order.platform}</Descriptions.Item>
          <Descriptions.Item label="买家">{order.buyer_name}</Descriptions.Item>
          <Descriptions.Item label="总金额">¥{(order.total_amount || 0).toFixed(2)}</Descriptions.Item>
          <Descriptions.Item label="实付金额">¥{(order.pay_amount || 0).toFixed(2)}</Descriptions.Item>
          <Descriptions.Item label="收件人">{order.receiver_name}</Descriptions.Item>
          <Descriptions.Item label="收件电话">{order.receiver_phone}</Descriptions.Item>
          <Descriptions.Item label="收件地址" span={2}>
            {order.receiver_province} {order.receiver_city} {order.receiver_district} {order.receiver_address}
          </Descriptions.Item>
          <Descriptions.Item label="买家留言" span={2}>{order.buyer_message || '-'}</Descriptions.Item>
          <Descriptions.Item label="卖家备注" span={2}>{order.seller_remark || '-'}</Descriptions.Item>
          <Descriptions.Item label="下单时间">{order.platform_created_at ? new Date(order.platform_created_at).toLocaleString('zh-CN') : '-'}</Descriptions.Item>
          <Descriptions.Item label="支付时间">{order.platform_paid_at ? new Date(order.platform_paid_at).toLocaleString('zh-CN') : '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="商品明细" style={{ marginTop: 16 }}>
        <Table rowKey="id" columns={itemColumns} dataSource={order.items || []} pagination={false} size="small" />
      </Card>

      {order.logistics && (
        <Card title="物流信息" style={{ marginTop: 16 }}>
          <Descriptions bordered column={2} size="small">
            <Descriptions.Item label="快递公司">{order.logistics.shipping_company}</Descriptions.Item>
            <Descriptions.Item label="快递单号">{order.logistics.tracking_no}</Descriptions.Item>
            <Descriptions.Item label="物流状态">{order.logistics.status}</Descriptions.Item>
            <Descriptions.Item label="最新信息">{order.logistics.latest_info || '-'}</Descriptions.Item>
          </Descriptions>
        </Card>
      )}
    </div>
  )
}
