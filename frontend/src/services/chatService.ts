import type {
  ChatHistoryMessage,
  ChatSession,
  ChatSseEvent,
  SendChatMessagePayload,
} from '../types/api'

import apiClient from './apiClient'

const textDecoder = new TextDecoder()

function parseSseFrame(frame: string): ChatSseEvent | null {
  const lines = frame
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  if (lines.length === 0) {
    return null
  }

  let eventName = ''
  const dataLines: string[] = []

  for (const line of lines) {
    if (line.startsWith('event:')) {
      eventName = line.slice('event:'.length).trim()
      continue
    }
    if (line.startsWith('data:')) {
      dataLines.push(line.slice('data:'.length).trim())
    }
  }

  if (!eventName || dataLines.length === 0) {
    return null
  }

  try {
    const data = JSON.parse(dataLines.join(''))
    if (eventName === 'token' || eventName === 'metadata' || eventName === 'done') {
      return { event: eventName, data } as ChatSseEvent
    }
    return null
  } catch {
    return {
      event: 'error',
      data: { message: '解析流式响应失败' },
    }
  }
}

export const chatService = {
  async listSessions(): Promise<ChatSession[]> {
    const response = await apiClient.get<ChatSession[]>('/chat/sessions')
    return response.data
  },

  async listMessages(sessionId: string): Promise<ChatHistoryMessage[]> {
    const response = await apiClient.get<ChatHistoryMessage[]>(`/chat/sessions/${sessionId}/messages`)
    return response.data
  },

  async streamMessage(
    payload: SendChatMessagePayload,
    onEvent: (event: ChatSseEvent) => void
  ): Promise<void> {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/v1/chat/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      let message = `请求失败（${response.status}）`
      try {
        const errorData = (await response.json()) as { detail?: string }
        if (errorData?.detail) {
          message = errorData.detail
        }
      } catch {
        // ignore json parse failure
      }
      onEvent({ event: 'error', data: { message } })
      return
    }

    if (!response.body) {
      onEvent({ event: 'error', data: { message: '服务器未返回流式内容' } })
      return
    }

    const reader = response.body.getReader()
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) {
        break
      }

      buffer += textDecoder.decode(value, { stream: true })
      const frames = buffer.split('\n\n')
      buffer = frames.pop() ?? ''

      for (const frame of frames) {
        const parsed = parseSseFrame(frame)
        if (parsed) {
          onEvent(parsed)
        }
      }
    }

    if (buffer.trim()) {
      const parsed = parseSseFrame(buffer)
      if (parsed) {
        onEvent(parsed)
      }
    }
  },
}
