import { FormEvent, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import useChatStore from '../stores/useChatStore'
import usePlanStore from '../stores/usePlanStore'

export default function DailyClearancePage() {
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const { sessionId, messages, isStreaming, taskCreatedHintTaskId, error, actions } = useChatStore()
  const setFocusedTaskId = usePlanStore((state) => state.actions.setFocusedTaskId)

  useEffect(() => {
    void actions.bootstrapLatestSession()
  }, [actions])

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!input.trim()) {
      return
    }
    const next = input
    setInput('')
    await actions.sendMessage(next)
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 md:px-8">
      <div className="max-w-4xl mx-auto h-[calc(100vh-6rem)] bg-white border border-slate-200 rounded-2xl flex flex-col">
        <header className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-slate-900">艾乐对话</h1>
            <p className="text-xs text-slate-500">{sessionId ? `会话：${sessionId}` : '新会话'}</p>
          </div>
          <button
            onClick={() => navigate('/execution')}
            className="text-sm rounded-lg border border-slate-300 px-3 py-1.5 text-slate-700"
          >
            查看任务
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {messages.length === 0 && (
            <p className="text-sm text-slate-500">今天学得怎么样？把你卡住的问题告诉艾乐吧。</p>
          )}

          {messages.map((item, index) => {
            const isUser = item.role === 'user'
            return (
              <div
                key={`${item.created_at}-${index}`}
                className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                    isUser
                      ? 'bg-indigo-600 text-white rounded-br-md'
                      : 'bg-slate-100 text-slate-800 rounded-bl-md'
                  }`}
                >
                  {item.content}
                </div>
              </div>
            )
          })}

          {taskCreatedHintTaskId && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 flex items-center justify-between gap-3">
              <p className="text-sm text-emerald-800">已为你创建学习任务，去任务页继续学习吧。</p>
              <button
                onClick={() => {
                  setFocusedTaskId(taskCreatedHintTaskId)
                  actions.clearTaskHint()
                  navigate('/execution')
                }}
                className="shrink-0 text-sm rounded-lg bg-emerald-600 text-white px-3 py-1.5"
              >
                立即查看
              </button>
            </div>
          )}

          {isStreaming && <p className="text-xs text-slate-500">艾乐正在思考...</p>}
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        <form onSubmit={onSubmit} className="border-t border-slate-200 p-4 flex gap-3">
          <input
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-200"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="输入你的问题，例如：我不懂三角函数定义"
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={isStreaming || !input.trim()}
            className="rounded-lg bg-indigo-600 text-white px-5 py-2 disabled:opacity-50"
          >
            发送
          </button>
        </form>
      </div>
    </div>
  )
}
