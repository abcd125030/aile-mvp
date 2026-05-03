import { create } from 'zustand'

import { planService } from '../services/planService'
import type { LearningPlan, LearningTask } from '../types/api'

interface GroupedTasks {
  in_progress: LearningTask[]
  pending: LearningTask[]
  completed: LearningTask[]
}

interface PlanState {
  currentPlan: LearningPlan | null
  groupedTasks: GroupedTasks
  focusedTaskId: string | null
  isLoading: boolean
  error: string | null
  actions: {
    fetchCurrentPlanAndTasks: () => Promise<void>
    setFocusedTaskId: (taskId: string | null) => void
    patchTask: (task: LearningTask) => void
  }
}

const emptyGroupedTasks = (): GroupedTasks => ({
  in_progress: [],
  pending: [],
  completed: [],
})

const groupTasks = (tasks: LearningTask[]): GroupedTasks => {
  const grouped = emptyGroupedTasks()
  for (const task of tasks) {
    if (task.status === 'in_progress') {
      grouped.in_progress.push(task)
      continue
    }
    if (task.status === 'pending') {
      grouped.pending.push(task)
      continue
    }
    grouped.completed.push(task)
  }
  return grouped
}

const flattenGroupedTasks = (groupedTasks: GroupedTasks): LearningTask[] => [
  ...groupedTasks.in_progress,
  ...groupedTasks.pending,
  ...groupedTasks.completed,
]

export const usePlanStore = create<PlanState>((set) => ({
  currentPlan: null,
  groupedTasks: emptyGroupedTasks(),
  focusedTaskId: null,
  isLoading: false,
  error: null,
  actions: {
    fetchCurrentPlanAndTasks: async () => {
      set({ isLoading: true, error: null })
      try {
        const plans = await planService.listPlans()
        const activePlan = plans.find((plan) => plan.status === 'active') ?? plans[0] ?? null

        if (!activePlan) {
          set({
            currentPlan: null,
            groupedTasks: emptyGroupedTasks(),
            isLoading: false,
          })
          return
        }

        const tasks = await planService.listTasks({ plan_id: activePlan.id })
        set({
          currentPlan: activePlan,
          groupedTasks: groupTasks(tasks),
          isLoading: false,
        })
      } catch (error) {
        const message = error instanceof Error ? error.message : '获取学习计划失败'
        set({
          error: message,
          isLoading: false,
        })
      }
    },

    setFocusedTaskId: (taskId: string | null) => {
      set({ focusedTaskId: taskId })
    },

    patchTask: (task: LearningTask) => {
      set((state) => {
        const allTasks = flattenGroupedTasks(state.groupedTasks)
        const nextTasks = allTasks.some((item) => item.id === task.id)
          ? allTasks.map((item) => (item.id === task.id ? task : item))
          : [...allTasks, task]
        return { groupedTasks: groupTasks(nextTasks) }
      })
    },
  },
}))

export default usePlanStore
