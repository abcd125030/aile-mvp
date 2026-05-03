import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import AileAvatar from '../components/ui/AileAvatar'
import EmptyState from '../components/ui/EmptyState'
import SkeletonBlock from '../components/ui/SkeletonBlock'
import usePlanStore from '../stores/usePlanStore'
import useUserStore from '../stores/useUserStore'

export default function HomePage() {
  const navigate = useNavigate()
  const user = useUserStore((state) => state.user)
  const fetchProfile = useUserStore((state) => state.actions.fetchProfile)
  const { currentPlan, groupedTasks, isLoading, error, actions } = usePlanStore()

  useEffect(() => {
    void fetchProfile()
    void actions.fetchCurrentPlanAndTasks()
  }, [actions, fetchProfile])

  const currentTask = groupedTasks.in_progress[0] ?? groupedTasks.pending[0] ?? null
  const targetUniversity = user?.target_university ?? '待设置'
  const scoreGap = Number((user?.settings?.target_score_gap as number | undefined) ?? 35)
  const countdownDays = Number((user?.settings?.exam_countdown_days as number | undefined) ?? 240)

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 md:px-8 aile-page-enter">
      <div className="max-w-4xl mx-auto space-y-6">
        <section className="aile-card p-6">
          <p className="text-sm text-slate-500">目标院校</p>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">{targetUniversity}</h1>
          <div className="mt-4 flex flex-wrap gap-3">
            <span className="inline-flex items-center rounded-full bg-indigo-50 text-indigo-700 px-3 py-1 text-sm">
              差距分数 {scoreGap} 分
            </span>
            <span className="inline-flex items-center rounded-full bg-emerald-50 text-emerald-700 px-3 py-1 text-sm">
              倒计时 {countdownDays} 天
            </span>
          </div>
        </section>

        <section className="aile-card p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500">当前学习任务</p>
              <h2 className="text-xl font-semibold text-slate-900 mt-1">
                {currentTask ? currentTask.title : '还没有待完成任务'}
              </h2>
              <p className="text-sm text-slate-600 mt-2">
                {currentTask
                  ? `类型：${currentTask.type} · 知识点 ${currentTask.knowledge_point_ids.join('、') || '-'}`
                  : '去和艾乐聊聊今天的学习困惑，系统会为你生成任务。'}
              </p>
            </div>
            <button
              onClick={() => navigate('/daily-clearance')}
              className="shrink-0 rounded-lg bg-indigo-600 text-white px-4 py-2 text-sm inline-flex items-center gap-2"
            >
              <AileAvatar size={20} />
              打开艾乐
            </button>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => {
                if (currentTask) {
                  actions.setFocusedTaskId(currentTask.id)
                }
                navigate(currentTask ? `/execution?taskId=${currentTask.id}` : '/execution')
              }}
              className="rounded-lg border border-indigo-200 text-indigo-700 bg-indigo-50 px-4 py-2 text-sm"
            >
              听讲解
            </button>
            <button
              onClick={() => {
                if (currentTask) {
                  actions.setFocusedTaskId(currentTask.id)
                }
                navigate(currentTask ? `/execution?taskId=${currentTask.id}` : '/execution')
              }}
              className="rounded-lg border border-slate-300 text-slate-700 px-4 py-2 text-sm"
            >
              做练习
            </button>
            <button
              onClick={() => navigate('/execution')}
              className="rounded-lg border border-slate-300 text-slate-700 px-4 py-2 text-sm"
            >
              我的计划
            </button>
          </div>
        </section>

        {isLoading && (
          <section className="aile-card p-6 space-y-3">
            <SkeletonBlock className="h-4 w-32" />
            <SkeletonBlock className="h-10 w-full" />
            <SkeletonBlock className="h-10 w-5/6" />
          </section>
        )}
        {error && <p className="text-sm text-red-600">{error}</p>}
        {!isLoading && !currentPlan && (
          <EmptyState
            title="还没有学习计划"
            description="去和艾乐聊聊今天的学习困惑，系统会自动生成你的学习任务。"
            actionLabel="前往艾乐对话"
            onAction={() => navigate('/daily-clearance')}
          />
        )}
        {currentPlan && (
          <p className="text-sm text-slate-500">
            当前计划：{currentPlan.title}（{currentPlan.status}）
          </p>
        )}
      </div>
    </div>
  )
}
