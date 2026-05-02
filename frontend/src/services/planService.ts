import apiClient from './apiClient'
import type { LearningPlan, LearningTask, PlanDetailResponse } from '../types/api'

export const planService = {
  async listPlans(): Promise<LearningPlan[]> {
    const response = await apiClient.get<LearningPlan[]>('/plans')
    return response.data
  },

  async getPlanDetail(planId: string): Promise<PlanDetailResponse> {
    const response = await apiClient.get<PlanDetailResponse>(`/plans/${planId}`)
    return response.data
  },

  async listTasks(params?: { plan_id?: string; status?: string }): Promise<LearningTask[]> {
    const response = await apiClient.get<LearningTask[]>('/tasks', { params })
    return response.data
  },

  async updateTaskStatus(taskId: string, status: 'pending' | 'in_progress' | 'completed') {
    const response = await apiClient.put<LearningTask>(`/tasks/${taskId}/status`, { status })
    return response.data
  },
}
