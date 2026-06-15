/**
 * 任务进度展示组件
 */
import { Space, Spin, Typography } from 'antd'
import { LoadingOutlined, ThunderboltOutlined } from '@ant-design/icons'

const { Text } = Typography

interface TaskProgressProps {
  progress: string
  phase?: string
}

const phaseLabels: Record<string, string> = {
  intent: '意图识别',
  planning: '任务规划',
  execution: '任务执行',
  review: '结果验收',
  done: '完成',
}

export default function TaskProgress({ progress, phase }: TaskProgressProps) {
  if (!progress) return null

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '8px 12px',
        background: '#f0f5ff',
        borderRadius: 8,
        margin: '0 0 12px',
      }}
    >
      <Spin indicator={<LoadingOutlined spin />} size="small" />
      <Text type="secondary" style={{ fontSize: 13 }}>
        {phase && (
          <Space size={4}>
            <ThunderboltOutlined />
            <span>{phaseLabels[phase] || phase}</span>
            <span>·</span>
          </Space>
        )}
        {progress}
      </Text>
    </div>
  )
}
