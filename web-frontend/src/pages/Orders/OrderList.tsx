import { useEffect, useState } from 'react'
import { Table, Card, Tag, Space, Button, Input, Select, DatePicker, Modal, Form, message } from 'antd'
import { SearchOutlined, SendOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { orderApi } from '../../services/api'
import type { Order, OrderFilter } from '../../types'

const { RangePicker } = DatePicker

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待付款' },
  paid: { color: 'orange', text: '待发货' },
  shipped: { color: 'blue', text: '已发货' },
  delivered: { color: 'cyan', text: '已签收' },
  completed: { color: 'green', text: '已完成' },
  closed: { color: 'red', text: '已关闭' },
  refunding: { color: 'purple', text: '退款中' },
}

const platformMap: Record<string, string> = {
  taobao: '淘宝', jd: '京东', pdd: '拼多多',
}

export default function OrderList() {
  const navigate = useNavigate()
  const [data, setData] = useState<Order[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [filters, setFilters] = useState<Partial<OrderFilter>>({})
  const [shipModal, setShipModal] = useState<{ visible: boolean; orderId: number | null }>({ visible: false, orderId: null })
  const [form] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await orderApi.list({ page, page_size: pageSize, ...filters } as OrderFilter)
      setData(res.data?.list || [])
      setTotal(res.data?.total || 0)
    } catch (e) {
      console.error('Failed to fetch orders:', e)
      message.error('订单列表加载失败，请稍后重试')
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [page, pageSize])

  const handleSearch = () => { setPage(1); fetchData() }

  const handleShip = async (values: { shipping_company: string; tracking_no: string }) => {
    if (!shipModal.orderId) return
    try {
      await orderApi.ship(shipModal.orderId, values)
      message.success('发货成功')
      setShipModal({ visible: false, orderId: null })
      form.resetFields()
      fetchData()
    } catch (e) {
      console.error('Failed to ship:', e)
      message.error('发货失败，请稍后重试')
    }
  }

  const columns = [
    { title: '订单号', dataIndex: 'order_no', width: 180, ellipsis: true },
    { title: '平台订单号', dataIndex: 'platform_order_no', width: 180, ellipsis: true },
    {
      title: '平台', dataIndex: 'platform', width: 80,
      render: (v: string) => <Tag>{platformMap[v] || v}</Tag>,
    },
    {
      title: '商品', width: 200, ellipsis: true,
      render: (_: unknown, r: Order) => r.items?.map((i) => i.product_name).join(', ') || '-',
    },
    { title: '买家', dataIndex: 'buyer_name', width: 100 },
    {
      title: '金额', dataIndex: 'pay_amount', width: 100, align: 'right' as const,
      render: (v: number) => `¥${(v || 0).toFixed(2)}`,
    },
    {
      title: '状态', dataIndex: 'status', width: 100,
      render: (v: string) => {
        const s = statusMap[v] || { color: 'default', text: v }
        return <Tag color={s.color}>{s.text}</Tag>
      },
    },
    {
      title: '下单时间', dataIndex: 'platform_created_at', width: 170,
      render: (v: string) => v ? new Date(v).toLocaleString('zh-CN') : '-',
    },
    {
      title: '操作', width: 180, fixed: 'right' as const,
      render: (_: unknown, record: Order) => (
        <Space>
          <Button type="link" size="small" onClick={() => navigate(`/orders/${record.id}`)}>详情</Button>
          {record.status === 'paid' && (
            <Button type="link" size="small" icon={<SendOutlined />}
              onClick={() => setShipModal({ visible: true, orderId: record.id })}>
              发货
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select placeholder="平台" allowClear style={{ width: 120 }}
            options={[{ value: 'taobao', label: '淘宝' }, { value: 'jd', label: '京东' }, { value: 'pdd', label: '拼多多' }]}
            onChange={(v) => setFilters((f) => ({ ...f, platform: v }))} />
          <Select placeholder="状态" allowClear style={{ width: 120 }}
            options={Object.entries(statusMap).map(([k, v]) => ({ value: k, label: v.text }))}
            onChange={(v) => setFilters((f) => ({ ...f, status: v }))} />
          <Input placeholder="搜索订单号/买家" allowClear style={{ width: 200 }}
            onChange={(e) => setFilters((f) => ({ ...f, keyword: e.target.value }))} />
          <RangePicker onChange={(dates) => setFilters((f) => ({
            ...f, date_from: dates?.[0]?.format('YYYY-MM-DD'), date_to: dates?.[1]?.format('YYYY-MM-DD')
          }))} />
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>搜索</Button>
        </Space>
      </Card>

      <Table
        rowKey="id" columns={columns} dataSource={data} loading={loading}
        scroll={{ x: 1400 }}
        pagination={{
          current: page, pageSize, total, showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
          onChange: (p, ps) => { setPage(p); setPageSize(ps) },
        }}
      />

      <Modal title="发货" open={shipModal.visible}
        onCancel={() => { setShipModal({ visible: false, orderId: null }); form.resetFields() }}
        onOk={() => form.submit()} okText="确认发货">
        <Form form={form} onFinish={handleShip} layout="vertical">
          <Form.Item name="shipping_company" label="快递公司" rules={[{ required: true }]}>
            <Select options={[
              { value: 'SF', label: '顺丰' }, { value: 'YTO', label: '圆通' },
              { value: 'ZTO', label: '中通' }, { value: 'STO', label: '申通' },
              { value: 'YD', label: '韵达' }, { value: 'JD', label: '京东物流' },
            ]} />
          </Form.Item>
          <Form.Item name="tracking_no" label="快递单号" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
