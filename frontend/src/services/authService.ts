import apiClient from './apiClient'
import type { LoginResponse, UserProfile } from '../types/api'

interface LoginPayload {
  phone: string
  sms_code: string
}

interface UpdateUserPayload {
  nickname?: string
  grade?: string
  textbook_version?: string
  target_university?: string
  settings?: Record<string, unknown>
}

export const authService = {
  async login(payload: LoginPayload): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', payload)
    return response.data
  },

  async fetchMe(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/users/me')
    return response.data
  },

  async updateMe(payload: UpdateUserPayload): Promise<UserProfile> {
    const response = await apiClient.put<UserProfile>('/users/me', payload)
    return response.data
  },
}
