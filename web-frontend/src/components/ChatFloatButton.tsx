/**
 * 浮动对话按钮 - 固定在右下角
 */
import { FloatButton } from 'antd'
import { RobotOutlined } from '@ant-design/icons'
import { useChatStore } from '../stores/useChatStore'
import ChatPanel from '../pages/Chat/ChatPanel'

export default function ChatFloatButton() {
  const toggle = useChatStore((s) => s.toggle)

  return (
    <>
      <FloatButton
        icon={<RobotOutlined />}
        type="primary"
        tooltip="AI 智能助手"
        onClick={toggle}
        style={{ right: 24, bottom: 24, width: 56, height: 56 }}
      />
      <ChatPanel />
    </>
  )
}
