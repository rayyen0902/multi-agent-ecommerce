import { useEffect, useState } from 'react'
import { Table, Card, Tag, message } from 'antd'
import { logisticsApi } from '../../services/api'
import type { LogisticsInfo } from '../../types'

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待发货' },
  in_transit: { color: 'blue', text: '运输中' },
  delivered: { color: 'cyan', text: '已派送' },
  signed: { color: 'green', text: '已签收' },
}

export default function LogisticsList() {
  const [data, setData] = useState<LogisticsInfo[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await logisticsApi.list({ page, page_size: 20 })
      setData(res.data?.list || [])
      setTotal(res.data?.total || 0)
    } catch (e) {
      console.error('Failed to fetch logistics:', e)
      message.error('物流列表加载失败，请稍后重试')
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [page])

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '订单ID', dataIndex: 'order_id', width: 100 },
    { title: '快递公司', dataIndex: 'shipping_company' },
    { title: '快递单号', dataIndex: 'tracking_no' },
    {
      title: '状态', dataIndex: 'status',
      render: (v: string) => {
        const s = statusMap[v] || { color: 'default', text: v }
        return <Tag color={s.color}>{s.text}</Tag>
      },
    },
    { title: '最新信息', dataIndex: 'latest_info', ellipsis: true },
    {
      title: '发货时间', dataIndex: 'shipped_at',
      render: (v: string) => v ? new Date(v).toLocaleString('zh-CN') : '-',
    },
  ]

  return (
    <Card title="物流跟踪">
      <Table rowKey="id" columns={columns} dataSource={data} loading={loading}
        pagination={{ current: page, total, onChange: setPage }} />
    </Card>
  )
}
