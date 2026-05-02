import { create } from 'zustand'

import { authService } from '../services/authService'
import type { UserProfile } from '../types/api'

interface ProfileDraft {
  grade: string
  textbook_version: string
  target_university: string
}

interface UserState {
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  needsOnboarding: boolean
  actions: {
    login: (phone: string, smsCode: string) => Promise<void>
    fetchProfile: () => Promise<void>
    completeOnboarding: (draft: ProfileDraft) => Promise<void>
    logout: () => void
  }
}

const storedToken = localStorage.getItem('token')

const hasMissingProfile = (user: UserProfile): boolean =>
  !user.grade || !user.textbook_version || !user.target_university

export const useUserStore = create<UserState>((set, get) => ({
  user: null,
  token: storedToken,
  isAuthenticated: storedToken !== null,
  isLoading: false,
  error: null,
  needsOnboarding: false,
  actions: {
    login: async (phone: string, smsCode: string) => {
      set({ isLoading: true, error: null })
      try {
        const response = await authService.login({ phone, sms_code: smsCode })
        localStorage.setItem('token', response.token)
        const requiresOnboarding = response.is_new_user || hasMissingProfile(response.user)

        set({
          token: response.token,
          user: response.user,
          isAuthenticated: true,
          needsOnboarding: requiresOnboarding,
          isLoading: false,
        })

        await get().actions.fetchProfile()
      } catch (error) {
        const message = error instanceof Error ? error.message : '登录失败，请稍后重试'
        set({
          error: message,
          isLoading: false,
          isAuthenticated: false,
        })
        throw error
      }
    },

    fetchProfile: async () => {
      if (!get().token) {
        return
      }

      set({ isLoading: true, error: null })
      try {
        const user = await authService.fetchMe()
        set({
          user,
          isLoading: false,
          needsOnboarding: hasMissingProfile(user),
        })
      } catch (error) {
        const message = error instanceof Error ? error.message : '获取用户信息失败'
        set({ error: message, isLoading: false })
        throw error
      }
    },

    completeOnboarding: async (draft: ProfileDraft) => {
      set({ isLoading: true, error: null })
      try {
        const user = await authService.updateMe(draft)
        set({
          user,
          needsOnboarding: hasMissingProfile(user),
          isLoading: false,
        })
      } catch (error) {
        const message = error instanceof Error ? error.message : '保存画像失败'
        set({ error: message, isLoading: false })
        throw error
      }
    },

    logout: () => {
      localStorage.removeItem('token')
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        needsOnboarding: false,
        error: null,
      })
    },
  },
}))

export default useUserStore
