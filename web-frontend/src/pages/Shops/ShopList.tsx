import { useEffect, useState } from 'react'
import { Table, Card, Tag, Button, Space, Modal, Form, Input, Select, message } from 'antd'
import { PlusOutlined, SyncOutlined } from '@ant-design/icons'
import { shopApi } from '../../services/api'
import type { Shop } from '../../types'

const platformMap: Record<string, string> = { taobao: '淘宝', jd: '京东', pdd: '拼多多' }

export default function ShopList() {
  const [data, setData] = useState<Shop[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await shopApi.list({ page, page_size: 20 })
      setData(res.data?.list || [])
      setTotal(res.data?.total || 0)
    } catch (e) {
      console.error('Failed to fetch shops:', e)
      message.error('店铺列表加载失败，请稍后重试')
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [page])

  const handleCreate = async (values: { name: string; platform: string; app_key: string; app_secret: string }) => {
    try {
      await shopApi.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      fetchData()
    } catch (e) {
      console.error('Failed to create shop:', e)
      message.error('创建失败，请稍后重试')
    }
  }

  const handleSync = async (id: number) => {
    try {
      await shopApi.triggerSync(id)
      message.success('同步任务已触发')
    } catch (e) {
      console.error('Failed to trigger sync:', e)
      message.error('触发同步失败，请稍后重试')
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '店铺名称', dataIndex: 'name' },
    { title: '平台', dataIndex: 'platform', render: (v: string) => <Tag>{platformMap[v] || v}</Tag> },
    { title: '状态', dataIndex: 'status', render: (v: number) => <Tag color={v === 1 ? 'green' : 'red'}>{v === 1 ? '正常' : '禁用'}</Tag> },
    { title: '自动同步', dataIndex: 'sync_enabled', render: (v: boolean) => v ? '是' : '否' },
    { title: '同步间隔', dataIndex: 'sync_interval_minutes', render: (v: number) => `${v} 分钟` },
    {
      title: '操作', width: 200,
      render: (_: unknown, r: Shop) => (
        <Space>
          <Button type="link" size="small" icon={<SyncOutlined />} onClick={() => handleSync(r.id)}>同步</Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card title="店铺管理" extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>添加店铺</Button>
      }>
        <Table rowKey="id" columns={columns} dataSource={data} loading={loading}
          pagination={{ current: page, total, onChange: setPage }} />
      </Card>

      <Modal title="添加店铺" open={modalVisible} onCancel={() => setModalVisible(false)} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="店铺名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="platform" label="平台" rules={[{ required: true }]}>
            <Select options={[
              { value: 'taobao', label: '淘宝' }, { value: 'jd', label: '京东' }, { value: 'pdd', label: '拼多多' },
            ]} />
          </Form.Item>
          <Form.Item name="app_key" label="App Key"><Input /></Form.Item>
          <Form.Item name="app_secret" label="App Secret"><Input.Password /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
