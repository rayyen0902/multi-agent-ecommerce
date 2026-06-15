import { useEffect, useState } from 'react'
import { Table, Card, Tag } from 'antd'
import { message } from 'antd'
import { productApi } from '../../services/api'
import type { Product } from '../../types'

export default function ProductList() {
  const [data, setData] = useState<Product[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await productApi.list({ page, page_size: 20 })
      setData(res.list || [])
      setTotal(res.total || 0)
    } catch (e) {
      console.error('Failed to fetch products:', e)
      message.error('商品列表加载失败，请稍后重试')
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [page])

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '商品名称', dataIndex: 'name', ellipsis: true },
    { title: '规格', dataIndex: 'sku_name', ellipsis: true },
    { title: '售价', dataIndex: 'price', render: (v: number) => `¥${(v || 0).toFixed(2)}` },
    { title: '成本价', dataIndex: 'cost_price', render: (v: number) => `¥${(v || 0).toFixed(2)}` },
    {
      title: '库存', dataIndex: 'stock',
      render: (v: number, r: Product) => (
        <span style={{ color: v <= (r.stock_warning_threshold || 10) ? '#f5222d' : undefined }}>
          {v}
        </span>
      ),
    },
    { title: '预警阈值', dataIndex: 'stock_warning_threshold' },
    { title: '状态', dataIndex: 'status', render: (v: number) => <Tag color={v === 1 ? 'green' : 'default'}>{v === 1 ? '在售' : '下架'}</Tag> },
  ]

  return (
    <Card title="商品管理">
      <Table rowKey="id" columns={columns} dataSource={data} loading={loading}
        pagination={{ current: page, total, onChange: setPage }} />
    </Card>
  )
}
