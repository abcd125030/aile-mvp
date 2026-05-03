import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import EmptyState from '../components/ui/EmptyState'
import SkeletonBlock from '../components/ui/SkeletonBlock'
import { planService } from '../services/planService'
import usePlanStore from '../stores/usePlanStore'
import type { ExerciseItem, LearningTask, SubmitAnswerResponse, TaskDetailResponse } from '../types/api'

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

type AnswerMap = Record<string, string>
type ResultMap = Record<string, SubmitAnswerResponse>

function extractChoiceAnswer(option: string): string {
  const normalized = option.trim()
  const matched = normalized.match(/^([A-Za-z])(?:\s*[.、\)]\s*.*)?$/)
  return matched ? matched[1].toUpperCase() : normalized
}

function parseLearningSections(detail: TaskDetailResponse): Array<{ title: string; content: string }> {
  const manifest = detail.content_package?.manifest
  const manifestSections = Array.isArray((manifest as { sections?: unknown[] } | undefined)?.sections)
    ? ((manifest as { sections: Array<{ type?: string; content?: string }> }).sections ?? [])
    : []

  const toSectionContent = (type: string) =>
    manifestSections
      .filter((item) => item.type === type && typeof item.content === 'string')
      .map((item) => item.content as string)
      .join('\n\n')
      .trim()

  const conceptFromManifest = toSectionContent('concept') || toSectionContent('text')
  const exampleFromManifest = toSectionContent('example')
  const summaryFromManifest = toSectionContent('summary')

  const knowledgeSummary = detail.knowledge_points.map((item) => item.name).join('、') || '当前知识点'

  return [
    {
      title: '概念',
      content: conceptFromManifest || `本任务聚焦：${knowledgeSummary}。先理解核心定义与判定规则。`,
    },
    {
      title: '例题',
      content: exampleFromManifest || '请先阅读示例思路，再尝试右侧练习题进行迁移应用。',
    },
    {
      title: '总结',
      content: summaryFromManifest || '完成练习后回顾错误原因，归纳通用解题步骤。',
    },
  ]
}

function ExerciseCard({
  exercise,
  answer,
  submitting,
  result,
  onChangeAnswer,
  onSubmit,
}: {
  exercise: ExerciseItem
  answer: string
  submitting: boolean
  result: SubmitAnswerResponse | null
  onChangeAnswer: (next: string) => void
  onSubmit: () => void
}) {
  const isChoice = Array.isArray(exercise.options) && exercise.options.length > 0

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
      <h4 className="font-medium text-slate-900">{exercise.stem}</h4>

      {isChoice ? (
        <div className="grid gap-2">
          {exercise.options?.map((option) => {
            const normalizedOptionAnswer = extractChoiceAnswer(option)
            const isSelected = answer === normalizedOptionAnswer
            return (
              <button
                type="button"
                key={option}
                onClick={() => onChangeAnswer(normalizedOptionAnswer)}
                className={`rounded-lg border px-3 py-2 text-left text-sm ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-slate-300 bg-white text-slate-700'
                }`}
              >
                {option}
              </button>
            )
          })}
        </div>
      ) : (
        <input
          value={answer}
          onChange={(event) => onChangeAnswer(event.target.value)}
          placeholder="请输入答案"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-200"
        />
      )}

      <button
        type="button"
        onClick={onSubmit}
        disabled={submitting || !answer.trim()}
        className="rounded-lg bg-indigo-600 text-white px-3 py-1.5 text-sm disabled:opacity-50"
      >
        {submitting ? '提交中...' : '提交答案'}
      </button>

      {result && (
        <div
          className={`rounded-lg border p-3 text-sm ${
            result.is_correct
              ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
              : 'border-rose-200 bg-rose-50 text-rose-800'
          }`}
        >
          <p>{result.is_correct ? '回答正确，做得很好。' : '回答不正确，再看下解析。'}</p>
          <p className="mt-1">标准答案：{result.correct_answer}</p>
          {result.solution && <p className="mt-1">解析：{result.solution}</p>}
        </div>
      )}
    </article>
  )
}

export default function ExecutionPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const focusedTaskFromQuery = searchParams.get('taskId')
  const knowledgePointIdFromQuery = searchParams.get('knowledgePointId')
  const { currentPlan, groupedTasks, focusedTaskId, isLoading, error, actions } = usePlanStore()

  const [taskDetail, setTaskDetail] = useState<TaskDetailResponse | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)
  const [answers, setAnswers] = useState<AnswerMap>({})
  const [results, setResults] = useState<ResultMap>({})
  const [submittingExerciseId, setSubmittingExerciseId] = useState<string | null>(null)
  const [statusUpdating, setStatusUpdating] = useState(false)
  const [completionHint, setCompletionHint] = useState<string | null>(null)
  const [autoStartAttemptedTaskId, setAutoStartAttemptedTaskId] = useState<string | null>(null)

  useEffect(() => {
    void actions.fetchCurrentPlanAndTasks()
  }, [actions])

  const taskByKnowledgePoint =
    knowledgePointIdFromQuery
      ? [...groupedTasks.in_progress, ...groupedTasks.pending].find((task) =>
          task.knowledge_point_ids.includes(knowledgePointIdFromQuery)
        )?.id
      : null
  const fallbackTaskId = taskByKnowledgePoint ?? groupedTasks.in_progress[0]?.id ?? groupedTasks.pending[0]?.id ?? null
  const activeTaskId = focusedTaskId ?? focusedTaskFromQuery ?? fallbackTaskId

  useEffect(() => {
    if (focusedTaskFromQuery && focusedTaskFromQuery !== focusedTaskId) {
      actions.setFocusedTaskId(focusedTaskFromQuery)
    }
  }, [actions, focusedTaskFromQuery, focusedTaskId])

  useEffect(() => {
    if (!focusedTaskId && fallbackTaskId) {
      actions.setFocusedTaskId(fallbackTaskId)
    }
  }, [actions, fallbackTaskId, focusedTaskId])

  useEffect(() => {
    if (!activeTaskId) {
      setTaskDetail(null)
      return
    }

    let cancelled = false
    const loadDetail = async () => {
      setDetailLoading(true)
      setDetailError(null)
      try {
        const detail = await planService.getTaskDetail(activeTaskId)
        if (cancelled) {
          return
        }
        setTaskDetail(detail)
        setAnswers({})
        setResults({})
        setCompletionHint(null)
        setAutoStartAttemptedTaskId(null)
      } catch (e) {
        if (cancelled) {
          return
        }
        setDetailError(e instanceof Error ? e.message : '加载任务详情失败')
        setTaskDetail(null)
      } finally {
        if (!cancelled) {
          setDetailLoading(false)
        }
      }
    }
    void loadDetail()

    return () => {
      cancelled = true
    }
  }, [activeTaskId])

  useEffect(() => {
    const maybeStartTask = async () => {
      if (!taskDetail || taskDetail.task.status !== 'pending' || statusUpdating) {
        return
      }
      if (autoStartAttemptedTaskId === taskDetail.task.id) {
        return
      }
      setStatusUpdating(true)
      setAutoStartAttemptedTaskId(taskDetail.task.id)
      try {
        const updated = await planService.updateTaskStatus(taskDetail.task.id, 'in_progress')
        actions.patchTask(updated)
        setTaskDetail((prev) => (prev ? { ...prev, task: updated } : prev))
      } catch (e) {
        setDetailError(e instanceof Error ? e.message : '更新任务状态失败')
      } finally {
        setStatusUpdating(false)
      }
    }
    void maybeStartTask()
  }, [actions, autoStartAttemptedTaskId, statusUpdating, taskDetail])

  const learningSections = useMemo(() => (taskDetail ? parseLearningSections(taskDetail) : []), [taskDetail])

  const submitOneExercise = async (exercise: ExerciseItem) => {
    if (!taskDetail) {
      return
    }
    const answer = (answers[exercise.id] ?? '').trim()
    if (!answer) {
      return
    }
    setSubmittingExerciseId(exercise.id)
    setDetailError(null)
    try {
      const response = await planService.submitTaskAnswer(taskDetail.task.id, {
        exercise_id: exercise.id,
        answer,
      })
      setResults((prev) => ({ ...prev, [exercise.id]: response }))
      if (response.task_status === 'completed') {
        await actions.fetchCurrentPlanAndTasks()
        setTaskDetail((prev) =>
          prev
            ? {
                ...prev,
                task: {
                  ...prev.task,
                  status: 'completed',
                  completed_at: new Date().toISOString(),
                },
              }
            : prev
        )
        setCompletionHint('任务已完成，已同步到任务列表。')
      }
    } catch (e) {
      setDetailError(e instanceof Error ? e.message : '提交答案失败')
    } finally {
      setSubmittingExerciseId(null)
    }
  }

  const allTasks = useMemo(
    () => [...groupedTasks.in_progress, ...groupedTasks.pending, ...groupedTasks.completed],
    [groupedTasks]
  )

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 md:px-8 aile-page-enter">
      <div className="max-w-6xl mx-auto space-y-6">
        <section className="aile-card p-6">
          <p className="text-sm text-slate-500">当前计划</p>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">
            {currentPlan ? currentPlan.title : '暂无学习计划'}
          </h1>
          <p className="text-sm text-slate-600 mt-2">
            状态：{currentPlan?.status ?? '-'} · 版本：{currentPlan?.version ?? '-'}
          </p>
          {allTasks.length > 0 && (
            <p className="text-xs text-slate-500 mt-2">任务总数：{allTasks.length}，点击任务卡可进入学习闭环</p>
          )}
        </section>

        {isLoading && (
          <section className="aile-card p-6 space-y-3">
            <SkeletonBlock className="h-4 w-36" />
            <SkeletonBlock className="h-10 w-full" />
            <SkeletonBlock className="h-10 w-11/12" />
          </section>
        )}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {!isLoading && !currentPlan && (
          <EmptyState
            title="你还没有学习计划"
            description="先去和艾乐聊聊今天的问题，系统会为你生成可执行任务。"
            actionLabel="前往艾乐对话"
            onAction={() => navigate('/daily-clearance')}
          />
        )}

        {currentPlan && (
          <>
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
                    isFocused={task.id === activeTaskId}
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
                    isFocused={task.id === activeTaskId}
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
                    isFocused={task.id === activeTaskId}
                    onFocus={() => actions.setFocusedTaskId(task.id)}
                  />
                ))}
              </section>
            </div>

            <section className="grid gap-4 lg:grid-cols-2">
              <article className="aile-card p-5 space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs text-slate-500">学习讲解</p>
                    <h3 className="text-lg font-semibold text-slate-900 mt-1">
                      {taskDetail?.task.title ?? '请选择一个任务'}
                    </h3>
                    {taskDetail && (
                      <p className="text-xs text-slate-500 mt-1">
                        状态：{taskDetail.task.status} · 知识点：{taskDetail.task.knowledge_point_ids.join('、') || '-'}
                      </p>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      const query = taskDetail ? `?taskId=${taskDetail.task.id}` : ''
                      navigate(`/daily-clearance${query}`)
                    }}
                    className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700"
                  >
                    我有疑问
                  </button>
                </div>

                {detailLoading && <p className="text-sm text-slate-500">加载任务详情中...</p>}
                {detailError && <p className="text-sm text-red-600">{detailError}</p>}

                {!detailLoading && taskDetail && (
                  <div className="space-y-3">
                    {learningSections.map((section) => (
                      <div key={section.title} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                        <p className="text-xs font-semibold text-slate-600">{section.title}</p>
                        <p className="text-sm text-slate-700 mt-1 whitespace-pre-wrap">{section.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </article>

              <article className="rounded-2xl border border-slate-200 bg-slate-50 p-5 space-y-4">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-slate-900">练习区</h3>
                  {taskDetail && (
                    <span className="text-xs rounded-full bg-white border border-slate-200 px-2 py-1 text-slate-600">
                      题目 {taskDetail.exercises.length} 道
                    </span>
                  )}
                </div>

                {!taskDetail && <p className="text-sm text-slate-500">请选择任务开始学习。</p>}
                {taskDetail && taskDetail.exercises.length === 0 && (
                  <p className="text-sm text-slate-500">当前任务暂无练习题，可先阅读讲解内容。</p>
                )}

                {taskDetail?.exercises.map((exercise) => (
                  <ExerciseCard
                    key={exercise.id}
                    exercise={exercise}
                    answer={answers[exercise.id] ?? ''}
                    submitting={submittingExerciseId === exercise.id}
                    result={results[exercise.id] ?? null}
                    onChangeAnswer={(next) => setAnswers((prev) => ({ ...prev, [exercise.id]: next }))}
                    onSubmit={() => void submitOneExercise(exercise)}
                  />
                ))}

                {completionHint && (
                  <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
                    {completionHint}
                  </div>
                )}
              </article>
            </section>
          </>
        )}
      </div>
    </div>
  )
}
