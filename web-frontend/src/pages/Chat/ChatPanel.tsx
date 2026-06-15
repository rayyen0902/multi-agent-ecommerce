/**
 * 对话面板主组件（右侧抽屉式）
 */
import { useEffect, useRef } from 'react'
import { Drawer, Input, Button, Typography, Empty, Divider } from 'antd'
import { SendOutlined, DeleteOutlined } from '@ant-design/icons'
import { useChatStore } from '../../stores/useChatStore'
import { useAuthStore } from '../../stores/useAuthStore'
import MessageBubble from './MessageBubble'
import TaskProgress from './TaskProgress'
import QuickActions from './QuickActions'

const { TextArea } = Input
const { Title } = Typography

export default function ChatPanel() {
  const {
    isOpen, close, messages, isLoading, progress,
    connect, disconnect, sendMessage, clearMessages,
  } = useChatStore()
  const token = useAuthStore((s) => s.token)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 连接 WebSocket
  useEffect(() => {
    if (isOpen && token) {
      connect(token)
    }
    return () => {
      disconnect()
    }
  }, [isOpen, token])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, progress])

  const handleSend = () => {
    const input = document.getElementById('chat-input') as HTMLTextAreaElement
    const content = input?.value?.trim()
    if (!content || isLoading) return
    sendMessage(content)
    input.value = ''
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Drawer
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={5} style={{ margin: 0 }}>AI 智能助手</Title>
          <Button
            type="text"
            size="small"
            icon={<DeleteOutlined />}
            onClick={clearMessages}
            disabled={messages.length === 0}
          >
            清空
          </Button>
        </div>
      }
      placement="right"
      width={420}
      open={isOpen}
      onClose={close}
      styles={{
        body: {
          display: 'flex',
          flexDirection: 'column',
          padding: 0,
          height: '100%',
        },
      }}
    >
      {/* 消息区域 */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '12px 16px',
        }}
      >
        {messages.length === 0 && !isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Empty
              description="开始与 AI 助手对话"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
            <QuickActions onAction={sendMessage} disabled={isLoading} />
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && (
              <TaskProgress progress={progress} />
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <Divider style={{ margin: 0 }} />

      {/* 输入区域 */}
      <div style={{ padding: '12px 16px' }}>
        {messages.length > 0 && (
          <QuickActions onAction={sendMessage} disabled={isLoading} />
        )}
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
          <TextArea
            id="chat-input"
            placeholder="输入您的问题...（Enter 发送，Shift+Enter 换行）"
            autoSize={{ minRows: 1, maxRows: 4 }}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={isLoading}
            style={{ height: 40 }}
          />
        </div>
      </div>
    </Drawer>
  )
}
