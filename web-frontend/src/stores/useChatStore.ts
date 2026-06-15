/**
 * 对话状态管理
 */
import { create } from 'zustand'
import { chatWebSocket, type ChatMessage } from '../services/chatApi'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  metadata?: ChatMessage['metadata']
}

interface ChatState {
  isOpen: boolean
  sessionId: string
  messages: Message[]
  isLoading: boolean
  progress: string

  open: () => void
  close: () => void
  toggle: () => void
  connect: (token: string) => void
  disconnect: () => void
  sendMessage: (content: string) => void
  clearMessages: () => void
}

let msgCounter = 0
const genId = () => `msg_${Date.now()}_${++msgCounter}`

export const useChatStore = create<ChatState>((set, get) => ({
  isOpen: false,
  sessionId: '',
  messages: [],
  isLoading: false,
  progress: '',

  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),
  toggle: () => set((s) => ({ isOpen: !s.isOpen })),

  connect: (token: string) => {
    chatWebSocket.connect(token, (msg: ChatMessage) => {
      const state = get()

      if (msg.type === 'agent_response') {
        set({
          messages: [
            ...state.messages,
            {
              id: genId(),
              role: 'assistant',
              content: msg.content,
              timestamp: msg.timestamp || Date.now(),
              metadata: msg.metadata,
            },
          ],
          isLoading: false,
          progress: '',
        })
      } else if (msg.type === 'task_progress') {
        set({
          progress: msg.content,
          sessionId: msg.session_id || state.sessionId,
        })
      } else if (msg.type === 'error') {
        set({
          messages: [
            ...state.messages,
            {
              id: genId(),
              role: 'system',
              content: `错误: ${msg.content}`,
              timestamp: msg.timestamp || Date.now(),
            },
          ],
          isLoading: false,
          progress: '',
        })
      }
    })
  },

  disconnect: () => {
    chatWebSocket.disconnect()
  },

  sendMessage: (content: string) => {
    const state = get()
    const sessionId = state.sessionId || crypto.randomUUID()

    // 添加用户消息
    set({
      sessionId,
      messages: [
        ...state.messages,
        {
          id: genId(),
          role: 'user',
          content,
          timestamp: Date.now(),
        },
      ],
      isLoading: true,
      progress: '正在处理...',
    })

    chatWebSocket.send(content, sessionId)
  },

  clearMessages: () => set({ messages: [], sessionId: '' }),
}))
