import { create } from 'zustand'

import { chatService } from '../services/chatService'
import type { ChatHistoryMessage, ChatSseEvent } from '../types/api'

interface ChatState {
  sessionId: string | null
  messages: ChatHistoryMessage[]
  isStreaming: boolean
  taskCreatedHintTaskId: string | null
  error: string | null
  actions: {
    bootstrapLatestSession: () => Promise<void>
    sendMessage: (message: string) => Promise<void>
    clearTaskHint: () => void
    reset: () => void
  }
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: null,
  messages: [],
  isStreaming: false,
  taskCreatedHintTaskId: null,
  error: null,
  actions: {
    bootstrapLatestSession: async () => {
      set({ error: null })
      const sessions = await chatService.listSessions()
      const latest = sessions[0]
      if (!latest) {
        set({ sessionId: null, messages: [] })
        return
      }
      const messages = await chatService.listMessages(latest.session_id)
      set({
        sessionId: latest.session_id,
        messages,
      })
    },

    sendMessage: async (message: string) => {
      const trimmed = message.trim()
      if (!trimmed || get().isStreaming) {
        return
      }

      const optimisticUserMessage: ChatHistoryMessage = {
        role: 'user',
        content: trimmed,
        created_at: new Date().toISOString(),
      }

      set((state) => ({
        messages: [...state.messages, optimisticUserMessage],
        isStreaming: true,
        error: null,
      }))

      let assistantBuffer = ''
      let assistantMessageCreated = false
      let latestMetadata: {
        intent?: string | null
        knowledge_point_ids?: string[]
        task_id?: string | null
      } = {}

      const handleEvent = (event: ChatSseEvent) => {
        if (event.event === 'token') {
          assistantBuffer += event.data.text
          if (!assistantMessageCreated) {
            assistantMessageCreated = true
            set((state) => ({
              messages: [
                ...state.messages,
                {
                  role: 'assistant',
                  content: assistantBuffer,
                  created_at: new Date().toISOString(),
                  intent: latestMetadata.intent ?? null,
                  knowledge_point_ids: latestMetadata.knowledge_point_ids,
                  task_id: latestMetadata.task_id ?? null,
                },
              ],
            }))
            return
          }

          set((state) => {
            const messages = [...state.messages]
            const lastIndex = messages.length - 1
            if (lastIndex >= 0 && messages[lastIndex].role === 'assistant') {
              messages[lastIndex] = {
                ...messages[lastIndex],
                content: assistantBuffer,
              }
            }
            return { messages }
          })
          return
        }

        if (event.event === 'metadata') {
          latestMetadata = {
            intent: event.data.intent,
            knowledge_point_ids: event.data.knowledge_point_ids,
            task_id: event.data.task_id,
          }
          set({
            sessionId: event.data.session_id,
            taskCreatedHintTaskId: event.data.task_created ? event.data.task_id : null,
          })
          set((state) => {
            const messages = [...state.messages]
            const lastIndex = messages.length - 1
            if (lastIndex >= 0 && messages[lastIndex].role === 'assistant') {
              messages[lastIndex] = {
                ...messages[lastIndex],
                intent: event.data.intent,
                knowledge_point_ids: event.data.knowledge_point_ids,
                task_id: event.data.task_id,
              }
            }
            return { messages }
          })
          return
        }

        if (event.event === 'done') {
          set({ sessionId: event.data.session_id })
          return
        }

        if (event.event === 'error') {
          set({ error: event.data.message })
        }
      }

      try {
        await chatService.streamMessage(
          {
            session_id: get().sessionId ?? undefined,
            message: trimmed,
            journey: 'DAILY_CLEARANCE',
          },
          handleEvent
        )
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : '发送消息失败',
        })
      } finally {
        set({ isStreaming: false })
      }
    },

    clearTaskHint: () => set({ taskCreatedHintTaskId: null }),

    reset: () =>
      set({
        sessionId: null,
        messages: [],
        isStreaming: false,
        taskCreatedHintTaskId: null,
        error: null,
      }),
  },
}))

export default useChatStore
