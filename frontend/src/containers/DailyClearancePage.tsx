import { FormEvent, useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import AileAvatar from '../components/ui/AileAvatar'
import ThinkingDots from '../components/ui/ThinkingDots'
import { demoKnowledgePointNames, demoQuickPrompts } from '../mock/day6DemoData'
import useChatStore from '../stores/useChatStore'
import usePlanStore from '../stores/usePlanStore'

export default function DailyClearancePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const taskIdFromQuery = searchParams.get('taskId')
  const [input, setInput] = useState('')
  const [streamingSeconds, setStreamingSeconds] = useState(0)
  const { sessionId, messages, isStreaming, taskCreatedHintTaskId, error, actions } = useChatStore()
  const setFocusedTaskId = usePlanStore((state) => state.actions.setFocusedTaskId)

  useEffect(() => {
    void actions.bootstrapLatestSession()
  }, [actions])

  useEffect(() => {
    if (!isStreaming) {
      setStreamingSeconds(0)
      return
    }
    const timer = window.setInterval(() => {
      setStreamingSeconds((prev) => prev + 1)
    }, 1000)
    return () => {
      window.clearInterval(timer)
    }
  }, [isStreaming])

  const showSlowHint = useMemo(() => isStreaming && streamingSeconds >= 10, [isStreaming, streamingSeconds])

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!input.trim()) {
      return
    }
    const next = input
    setInput('')
    await actions.sendMessage(next)
  }

  const sendQuickPrompt = async (prompt: string) => {
    if (isStreaming) {
      return
    }
    setInput('')
    await actions.sendMessage(prompt)
  }

  return (
    <div className="min-h-screen bg-slate-50 px-3 py-4 md:px-8 md:py-6 aile-page-enter">
      <div className="max-w-5xl mx-auto h-[calc(100vh-5rem)] md:h-[calc(100vh-6rem)] aile-card flex flex-col">
        <header className="px-4 py-3 md:px-5 md:py-4 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AileAvatar size={36} />
            <div>
              <h1 className="text-lg font-semibold text-slate-900">艾乐对话</h1>
              <p className="text-xs text-slate-500">{sessionId ? `会话：${sessionId}` : '新会话'}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/execution')}
            className="text-sm rounded-lg border border-slate-300 px-3 py-1.5 text-slate-700 hover:bg-slate-50"
          >
            查看任务
          </button>
        </header>

        <div className="px-4 md:px-5 pt-3 border-b border-slate-100">
          <p className="text-xs text-slate-500 mb-2">快捷提问</p>
          <div className="flex flex-wrap gap-2 pb-3">
            {demoQuickPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => void sendQuickPrompt(prompt)}
                className="rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs text-indigo-700 hover:bg-indigo-100"
                disabled={isStreaming}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4 md:px-5 space-y-3">
          {taskIdFromQuery && (
            <div className="rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm text-indigo-800">
              正在围绕任务 {taskIdFromQuery} 继续答疑。
            </div>
          )}

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
                  {!isUser && (item.knowledge_point_ids?.length ?? 0) > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {item.knowledge_point_ids?.map((kpId) => (
                        <button
                          type="button"
                          key={`${item.created_at}-${kpId}`}
                          onClick={() => {
                            const taskId = item.task_id ?? taskCreatedHintTaskId
                            if (taskId) {
                              setFocusedTaskId(taskId)
                              navigate(`/execution?taskId=${taskId}`)
                              return
                            }
                            navigate(`/execution?knowledgePointId=${kpId}`)
                          }}
                          className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-xs text-emerald-700 hover:bg-emerald-100"
                        >
                          {demoKnowledgePointNames[kpId] ?? kpId}
                        </button>
                      ))}
                    </div>
                  )}
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
                  navigate(`/execution?taskId=${taskCreatedHintTaskId}`)
                }}
                className="shrink-0 text-sm rounded-lg bg-emerald-600 text-white px-3 py-1.5"
              >
                立即查看
              </button>
            </div>
          )}

          {isStreaming && (
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 text-xs text-slate-500">
                <ThinkingDots />
                艾乐正在思考...
              </div>
              {showSlowHint && (
                <p className="text-xs rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-amber-700">
                  艾乐正在思考，请稍候...
                </p>
              )}
            </div>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        <form onSubmit={onSubmit} className="border-t border-slate-200 p-3 md:p-4 flex gap-2 md:gap-3">
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
