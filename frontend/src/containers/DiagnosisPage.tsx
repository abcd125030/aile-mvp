import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import EmptyState from '../components/ui/EmptyState'
import SkeletonBlock from '../components/ui/SkeletonBlock'
import { appConfig } from '../config/appConfig'
import { demoDiagnosisReport } from '../mock/day6DemoData'
import { diagnosisService } from '../services/diagnosisService'
import { planService } from '../services/planService'
import usePlanStore from '../stores/usePlanStore'

export default function DiagnosisPage() {
  const navigate = useNavigate()
  const groupedTasks = usePlanStore((state) => state.groupedTasks)
  const isLoading = usePlanStore((state) => state.isLoading)
  const fetchCurrentPlanAndTasks = usePlanStore((state) => state.actions.fetchCurrentPlanAndTasks)
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const lastSavedSignatureRef = useRef<string | null>(null)
  const latestSavedReportIdRef = useRef<string | null>(null)

  useEffect(() => {
    void fetchCurrentPlanAndTasks()
  }, [fetchCurrentPlanAndTasks])

  const diagnosisSnapshot = useMemo(() => {
    if (appConfig.demoMode) {
      return {
        mode: 'demo' as const,
        weakPoints: demoDiagnosisReport.weaknesses.map((item) => ({
          id: item.id,
          label: item.name,
          count: Math.round((1 - item.mastery) * 5),
        })),
      }
    }

    const activePool = [...groupedTasks.pending, ...groupedTasks.in_progress]
    const reviewPool = [...groupedTasks.completed]
    const pool = activePool.length > 0 ? activePool : reviewPool
    const counts = new Map<string, number>()
    for (const task of pool) {
      for (const kp of task.knowledge_point_ids) {
        counts.set(kp, (counts.get(kp) ?? 0) + 1)
      }
    }

    return {
      mode: activePool.length > 0 ? ('active' as const) : reviewPool.length > 0 ? ('review' as const) : ('empty' as const),
      weakPoints: [...counts.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6)
        .map(([id, count]) => ({ id, label: id, count })),
    }
  }, [groupedTasks.completed, groupedTasks.in_progress, groupedTasks.pending])

  const weakPoints = diagnosisSnapshot.weakPoints
  const isReviewMode = diagnosisSnapshot.mode === 'review'

  const persistSimplifiedReport = async () => {
    if (appConfig.demoMode || weakPoints.length === 0) {
      return null
    }

    const signature = JSON.stringify({
      mode: diagnosisSnapshot.mode,
      weakPoints: weakPoints.map((item) => [item.id, item.count]),
    })
    if (lastSavedSignatureRef.current === signature && latestSavedReportIdRef.current) {
      return latestSavedReportIdRef.current
    }

    const savedReport = await diagnosisService.saveSimplifiedReport({
      title: isReviewMode ? '诊断报告（复盘版）' : '诊断报告（简化版）',
      source: isReviewMode ? 'active_plan_completed_tasks_review' : 'active_plan_pending_in_progress_tasks',
      weak_points: weakPoints.map((item) => ({
        id: item.id,
        name: item.label,
        pending_task_count: item.count,
      })),
    })
    lastSavedSignatureRef.current = signature
    latestSavedReportIdRef.current = savedReport.id
    return savedReport.id
  }

  useEffect(() => {
    let cancelled = false
    const persistReport = async () => {
      try {
        const reportId = await persistSimplifiedReport()
        if (cancelled || !reportId) {
          return
        }
      } catch {
        // Do not block diagnosis page rendering if persistence fails.
      }
    }

    void persistReport()
    return () => {
      cancelled = true
    }
  }, [diagnosisSnapshot.mode, weakPoints])

  const generatePlanFromWeakPoints = async () => {
    if (weakPoints.length === 0 || isGeneratingPlan) {
      return
    }
    setGenerateError(null)
    setIsGeneratingPlan(true)
    try {
      let reportId: string | null = null
      try {
        reportId = await persistSimplifiedReport()
      } catch {
        reportId = latestSavedReportIdRef.current
      }

      const generated = await planService.generatePlan({
        title: '诊断巩固计划',
        source: 'diagnosis',
        knowledge_point_ids: weakPoints.map((item) => item.id),
        set_as_current: true,
      })

      if (reportId) {
        try {
          await diagnosisService.bindGeneratedPlan(reportId, generated.plan.id)
        } catch {
          // Do not block plan generation navigation if binding fails.
        }
      }

      await fetchCurrentPlanAndTasks()
      const firstTaskId = generated.tasks[0]?.id
      navigate(firstTaskId ? `/execution?taskId=${firstTaskId}` : '/execution')
    } catch (error) {
      setGenerateError(error instanceof Error ? error.message : '生成巩固计划失败')
    } finally {
      setIsGeneratingPlan(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 md:px-8 aile-page-enter">
      <div className="max-w-5xl mx-auto space-y-6">
        <section className="aile-card p-6">
          <h1 className="text-2xl font-bold text-slate-900">
            {isReviewMode ? '诊断报告（复盘版）' : '诊断报告（简化版）'}
          </h1>
          {isReviewMode ? (
            <p className="text-sm text-slate-600 mt-2">
              当前计划任务已完成，基于已完成任务做复盘诊断，提取高频知识点用于下一轮巩固。
            </p>
          ) : (
            <p className="text-sm text-slate-600 mt-2">
              基于当前未完成任务，提取高频薄弱知识点，帮助你快速规划下一步巩固方向。
            </p>
          )}
          {appConfig.demoMode && (
            <p className="text-xs text-indigo-600 mt-2">
              演示模式：{demoDiagnosisReport.title} · 分数 {demoDiagnosisReport.score.total}/{demoDiagnosisReport.score.full}
            </p>
          )}
        </section>

        <section className="aile-card p-6">
          <h2 className="text-lg font-semibold text-slate-900">薄弱知识点列表</h2>

          {isLoading && !appConfig.demoMode ? (
            <div className="mt-4 space-y-2">
              <SkeletonBlock className="h-10 w-full" />
              <SkeletonBlock className="h-10 w-11/12" />
              <SkeletonBlock className="h-10 w-10/12" />
            </div>
          ) : weakPoints.length === 0 ? (
            <div className="mt-3">
              <EmptyState
                title="暂无诊断数据"
                description="当前计划暂无可用于诊断的任务，先去学习任务页完成一轮学习后再查看。"
                actionLabel="去学习任务页"
                onAction={() => navigate('/execution')}
              />
            </div>
          ) : (
            <ul className="mt-4 space-y-2">
              {weakPoints.map((item) => (
                <li
                  key={item.id}
                  className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900 flex items-center justify-between"
                >
                  <span>{item.label}</span>
                  <span>{isReviewMode ? '相关完成任务' : '待巩固任务'} {item.count} 个</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="aile-card p-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => void generatePlanFromWeakPoints()}
            disabled={weakPoints.length === 0 || isGeneratingPlan}
            className="rounded-lg bg-indigo-600 text-white px-4 py-2 text-sm"
          >
            {isGeneratingPlan ? '生成中...' : '生成巩固计划'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/daily-clearance')}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700"
          >
            去和艾乐讨论
          </button>
          {generateError && <p className="w-full text-sm text-red-600">{generateError}</p>}
        </section>
      </div>
    </div>
  )
}
