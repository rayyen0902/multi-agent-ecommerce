/**
 * 快捷操作按钮
 */
import { Button, Space } from 'antd'
import {
  BarChartOutlined,
  ThunderboltOutlined,
  MessageOutlined,
  PieChartOutlined,
  ShoppingCartOutlined,
} from '@ant-design/icons'

interface QuickActionsProps {
  onAction: (text: string) => void
  disabled?: boolean
}

const actions = [
  { icon: <ShoppingCartOutlined />, label: '今日订单概览', text: '帮我查看今天的订单概览数据' },
  { icon: <BarChartOutlined />, label: '销售趋势', text: '分析一下最近7天的销售趋势' },
  { icon: <ThunderboltOutlined />, label: '创建规则', text: '帮我创建一条自动化规则：当订单金额超过500元时自动标记为VIP' },
  { icon: <PieChartOutlined />, label: '平台对比', text: '对比各平台的订单数据和销售额' },
  { icon: <MessageOutlined />, label: '客服建议', text: '有个买家要求退款，帮我生成回复建议' },
]

export default function QuickActions({ onAction, disabled }: QuickActionsProps) {
  return (
    <div style={{ padding: '8px 0' }}>
      <Space wrap size={[8, 8]}>
        {actions.map((action) => (
          <Button
            key={action.label}
            size="small"
            icon={action.icon}
            disabled={disabled}
            onClick={() => onAction(action.text)}
          >
            {action.label}
          </Button>
        ))}
      </Space>
    </div>
  )
}
