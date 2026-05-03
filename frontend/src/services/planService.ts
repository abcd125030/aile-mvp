import apiClient from './apiClient'
import type {
  GeneratePlanPayload,
  LearningPlan,
  LearningTask,
  PlanDetailResponse,
  SubmitAnswerPayload,
  SubmitAnswerResponse,
  TaskDetailResponse,
} from '../types/api'

export const planService = {
  async listPlans(): Promise<LearningPlan[]> {
    const response = await apiClient.get<LearningPlan[]>('/plans')
    return response.data
  },

  async getPlanDetail(planId: string): Promise<PlanDetailResponse> {
    const response = await apiClient.get<PlanDetailResponse>(`/plans/${planId}`)
    return response.data
  },

  async generatePlan(payload: GeneratePlanPayload): Promise<PlanDetailResponse> {
    const response = await apiClient.post<PlanDetailResponse>('/plans/generate', payload)
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

  async getTaskDetail(taskId: string): Promise<TaskDetailResponse> {
    const response = await apiClient.get<TaskDetailResponse>(`/tasks/${taskId}`)
    return response.data
  },

  async submitTaskAnswer(taskId: string, payload: SubmitAnswerPayload): Promise<SubmitAnswerResponse> {
    const response = await apiClient.post<SubmitAnswerResponse>(`/tasks/${taskId}/submit-answer`, payload)
    return response.data
  },
}
