/**
 * WebSocket 对话服务
 */

export interface ChatMessage {
  type: 'user_message' | 'agent_response' | 'task_progress' | 'error'
  session_id: string
  content: string
  metadata?: {
    agent_name?: string
    task_id?: string
    progress?: number
    phase?: string
    result_data?: unknown
    intent?: Record<string, unknown>
  }
  timestamp?: number
}

type MessageHandler = (msg: ChatMessage) => void

export class ChatWebSocket {
  private ws: WebSocket | null = null
  private onMessage: MessageHandler | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null

  connect(token: string, handler: MessageHandler): void {
    this.onMessage = handler

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ecom/api/agent/ws?token=${encodeURIComponent(token)}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('[ChatWS] 连接成功')
    }

    this.ws.onmessage = (event) => {
      try {
        const msg: ChatMessage = JSON.parse(event.data)
        msg.timestamp = Date.now()
        this.onMessage?.(msg)
      } catch (e) {
        console.error('[ChatWS] 消息解析失败:', e)
      }
    }

    this.ws.onclose = (event) => {
      console.log('[ChatWS] 连接断开:', event.code)
      if (event.code !== 4001) {
        // 非认证失败，3秒后重连
        this.reconnectTimer = setTimeout(() => {
          this.connect(token, handler)
        }, 3000)
      }
    }

    this.ws.onerror = (error) => {
      console.error('[ChatWS] 错误:', error)
    }
  }

  send(content: string, sessionId: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'user_message',
        session_id: sessionId,
        content,
      }))
    } else {
      console.warn('[ChatWS] 未连接，无法发送消息')
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.onMessage = null
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const chatWebSocket = new ChatWebSocket()
