import { useEffect, useState } from 'react'
import { Table, Card, Tag } from 'antd'
import { productApi } from '../../services/api'

export default function ProductList() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res: any = await productApi.list({ page, page_size: 20 })
      setData(res.data?.list || [])
      setTotal(res.data?.total || 0)
    } catch (e) { /* handled */ }
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
      render: (v: number, r: any) => (
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
