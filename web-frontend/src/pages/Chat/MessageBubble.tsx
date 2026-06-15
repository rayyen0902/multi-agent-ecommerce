/**
 * 消息气泡组件
 */
import { Avatar, Typography } from 'antd'
import {
  RobotOutlined,
  UserOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'

const { Paragraph, Text } = Typography

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

const roleConfig = {
  user: {
    avatar: <UserOutlined />,
    avatarBg: '#1677ff',
    align: 'flex-end' as const,
    bubbleBg: '#e6f4ff',
    name: '你',
  },
  assistant: {
    avatar: <RobotOutlined />,
    avatarBg: '#52c41a',
    align: 'flex-start' as const,
    bubbleBg: '#f6ffed',
    name: 'AI 助手',
  },
  system: {
    avatar: <ExclamationCircleOutlined />,
    avatarBg: '#faad14',
    align: 'flex-start' as const,
    bubbleBg: '#fffbe6',
    name: '系统',
  },
}

export default function MessageBubble({ message }: { message: Message }) {
  const config = roleConfig[message.role]

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: config.align,
        marginBottom: 16,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
          maxWidth: '85%',
        }}
      >
        <Avatar
          size={32}
          style={{ backgroundColor: config.avatarBg, flexShrink: 0 }}
          icon={config.avatar}
        />
        <div
          style={{
            background: config.bubbleBg,
            borderRadius: 12,
            padding: '10px 14px',
            maxWidth: '100%',
            wordBreak: 'break-word',
          }}
        >
          <Paragraph
            style={{ margin: 0, whiteSpace: 'pre-wrap' }}
            ellipsis={false}
          >
            {message.content}
          </Paragraph>
        </div>
      </div>
      <Text
        type="secondary"
        style={{ fontSize: 11, marginTop: 4, padding: '0 44px' }}
      >
        {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </Text>
    </div>
  )
}
