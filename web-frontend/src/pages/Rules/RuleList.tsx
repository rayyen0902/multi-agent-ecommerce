import { useEffect, useState } from 'react'
import { Table, Card, Tag, Switch } from 'antd'
import { ruleApi } from '../../services/api'

const typeMap: Record<string, string> = {
  auto_ship: '自动发货', auto_review: '自动评价',
  stock_alert: '库存预警', custom: '自定义',
}

export default function RuleList() {
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res: any = await ruleApi.list({ page, page_size: 20 })
      setData(res.data?.list || [])
      setTotal(res.data?.total || 0)
    } catch (e) { /* handled */ }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [page])

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '规则名称', dataIndex: 'name' },
    { title: '类型', dataIndex: 'type', render: (v: string) => <Tag>{typeMap[v] || v}</Tag> },
    { title: '优先级', dataIndex: 'priority', width: 80 },
    { title: '启用', dataIndex: 'enabled', render: (v: boolean) => <Switch checked={v} disabled size="small" /> },
    { title: '触发次数', dataIndex: 'trigger_count', width: 100 },
    {
      title: '最后触发', dataIndex: 'last_triggered_at',
      render: (v: string) => v ? new Date(v).toLocaleString('zh-CN') : '-',
    },
  ]

  return (
    <Card title="自动化规则">
      <Table rowKey="id" columns={columns} dataSource={data} loading={loading}
        pagination={{ current: page, total, onChange: setPage }} />
    </Card>
  )
}
