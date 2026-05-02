import { useEffect } from 'react'

import type { LearningTask } from '../types/api'
import usePlanStore from '../stores/usePlanStore'

function TaskCard({
  task,
  isFocused,
  onFocus,
}: {
  task: LearningTask
  isFocused: boolean
  onFocus: () => void
}) {
  const estimatedMinutes =
    typeof task.metadata.estimated_minutes === 'number'
      ? task.metadata.estimated_minutes
      : null

  return (
    <button
      onClick={onFocus}
      className={`w-full text-left rounded-xl border p-4 transition ${
        isFocused ? 'border-indigo-400 bg-indigo-50' : 'border-slate-200 bg-white'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-medium text-slate-900">{task.title}</h3>
        <span className="text-xs rounded-full bg-slate-100 text-slate-600 px-2 py-1">{task.type}</span>
      </div>
      <p className="text-sm text-slate-600 mt-2">知识点：{task.knowledge_point_ids.join('、') || '-'}</p>
      <p className="text-xs text-slate-500 mt-2">预计时长：{estimatedMinutes ? `${estimatedMinutes} 分钟` : '待评估'}</p>
    </button>
  )
}

export default function ExecutionPage() {
  const { currentPlan, groupedTasks, focusedTaskId, isLoading, error, actions } = usePlanStore()

  useEffect(() => {
    void actions.fetchCurrentPlanAndTasks()
  }, [actions])

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 md:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        <section className="bg-white border border-slate-200 rounded-2xl p-6">
          <p className="text-sm text-slate-500">当前计划</p>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">
            {currentPlan ? currentPlan.title : '暂无学习计划'}
          </h1>
          <p className="text-sm text-slate-600 mt-2">
            状态：{currentPlan?.status ?? '-'} · 版本：{currentPlan?.version ?? '-'}
          </p>
        </section>

        {isLoading && <p className="text-sm text-slate-500">加载任务中...</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {!isLoading && !currentPlan && (
          <section className="bg-white border border-dashed border-slate-300 rounded-2xl p-6">
            <p className="text-slate-600">你还没有学习计划，先去和艾乐聊聊今天的问题吧。</p>
          </section>
        )}

        {currentPlan && (
          <div className="grid gap-4 md:grid-cols-3">
            <section className="space-y-3">
              <h2 className="text-sm font-semibold text-indigo-700">进行中</h2>
              {groupedTasks.in_progress.length === 0 && (
                <p className="text-sm text-slate-500 bg-white border border-slate-200 rounded-xl p-3">暂无任务</p>
              )}
              {groupedTasks.in_progress.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isFocused={task.id === focusedTaskId}
                  onFocus={() => actions.setFocusedTaskId(task.id)}
                />
              ))}
            </section>

            <section className="space-y-3">
              <h2 className="text-sm font-semibold text-amber-700">待完成</h2>
              {groupedTasks.pending.length === 0 && (
                <p className="text-sm text-slate-500 bg-white border border-slate-200 rounded-xl p-3">暂无任务</p>
              )}
              {groupedTasks.pending.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isFocused={task.id === focusedTaskId}
                  onFocus={() => actions.setFocusedTaskId(task.id)}
                />
              ))}
            </section>

            <section className="space-y-3">
              <h2 className="text-sm font-semibold text-emerald-700">已完成</h2>
              {groupedTasks.completed.length === 0 && (
                <p className="text-sm text-slate-500 bg-white border border-slate-200 rounded-xl p-3">暂无任务</p>
              )}
              {groupedTasks.completed.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isFocused={task.id === focusedTaskId}
                  onFocus={() => actions.setFocusedTaskId(task.id)}
                />
              ))}
            </section>
          </div>
        )}
      </div>
    </div>
  )
}
