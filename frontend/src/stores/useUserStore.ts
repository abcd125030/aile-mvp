import { create } from 'zustand'

import { authService } from '../services/authService'
import { planService } from '../services/planService'
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
const initialKnowledgePointIds = ['kp_func_mono', 'kp_trig_def', 'kp_derivative_concept']

const hasMissingProfile = (user: UserProfile): boolean =>
  !user.grade || !user.textbook_version || !user.target_university

async function ensureCurrentPlanForUser(
  user: UserProfile,
  options?: { force?: boolean; source?: string; title?: string }
): Promise<UserProfile> {
  if (hasMissingProfile(user)) {
    return user
  }
  if (!options?.force && user.current_plan_id) {
    return user
  }

  const generated = await planService.generatePlan({
    title: options?.title ?? '初始学习计划',
    source: options?.source ?? 'profile_backfill',
    knowledge_point_ids: initialKnowledgePointIds,
    set_as_current: true,
  })

  return {
    ...user,
    current_plan_id: generated.plan.id,
    current_plan_snapshot: {
      title: generated.plan.title,
      status: generated.plan.status,
    },
  }
}

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
        const userWithPlan = await ensureCurrentPlanForUser(user, {
          source: 'profile_backfill',
          title: '初始学习计划',
        })
        set({
          user: userWithPlan,
          isLoading: false,
          needsOnboarding: hasMissingProfile(userWithPlan),
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
        const userWithPlan = await ensureCurrentPlanForUser(user, {
          force: true,
          source: 'onboarding',
          title: '初始学习计划',
        })
        set({
          user: userWithPlan,
          needsOnboarding: hasMissingProfile(userWithPlan),
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
