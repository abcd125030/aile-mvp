export type TaskStatus = 'pending' | 'in_progress' | 'completed'

export interface CurrentPlanSnapshot {
  title: string
  status: string
}

export interface UserProfile {
  id: string
  phone: string | null
  nickname: string
  grade: string
  textbook_version: string
  target_university: string | null
  settings: Record<string, unknown>
  current_plan_id: string | null
  current_plan_snapshot: CurrentPlanSnapshot | null
}

export interface LoginResponse {
  user: UserProfile
  token: string
  is_new_user: boolean
}

export interface LearningTask {
  id: string
  plan_id: string
  title: string
  type: string
  status: TaskStatus
  source: string
  source_problem_id: string | null
  knowledge_point_ids: string[]
  metadata: Record<string, unknown>
  due_at: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export interface KnowledgePoint {
  id: string
  name: string
  description: string | null
  prerequisite_ids: string[]
  difficulty: number
  subject: string
  created_at: string
}

export interface ExerciseItem {
  id: string
  stem: string
  options: string[] | null
  knowledge_point_ids: string[]
  difficulty: number
  metadata: Record<string, unknown>
}

export interface ContentPackage {
  id: string
  status: string
  manifest: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface TaskDetailResponse {
  task: LearningTask
  knowledge_points: KnowledgePoint[]
  content_package: ContentPackage | null
  exercises: ExerciseItem[]
}

export interface SubmitAnswerPayload {
  exercise_id: string
  answer: string
}

export interface SubmitAnswerResponse {
  task_id: string
  exercise_id: string
  is_correct: boolean
  correct_answer: string
  solution: string | null
  task_status: TaskStatus
}

export interface LearningPlan {
  id: string
  user_id: string
  title: string
  status: 'active' | 'completed' | 'archived'
  version: number
  snapshot: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface PlanDetailResponse {
  plan: LearningPlan
  tasks: LearningTask[]
}

export interface GeneratePlanPayload {
  title?: string
  source?: string
  knowledge_point_ids: string[]
  set_as_current?: boolean
}

export interface SimplifiedWeakPointPayloadItem {
  id: string
  name: string
  pending_task_count: number
}

export interface SaveSimplifiedDiagnosisReportPayload {
  title?: string
  source?: string
  weak_points: SimplifiedWeakPointPayloadItem[]
}

export interface DiagnosisReport {
  id: string
  user_id: string
  title: string
  original_file_url: string | null
  summary: Record<string, unknown>
  detailed_analysis: Record<string, unknown>
  generated_plan_id: string | null
  created_at: string
}

export interface ChatSession {
  session_id: string
  last_message: string
  last_active_at: string
  message_count: number
}

export interface ChatHistoryMessage {
  role: 'user' | 'assistant' | string
  content: string
  created_at: string
  intent?: string | null
  knowledge_point_ids?: string[]
  task_id?: string | null
}

export interface SendChatMessagePayload {
  session_id?: string
  message: string
  journey?: string
}

export interface ChatSseTokenEvent {
  event: 'token'
  data: {
    text: string
  }
}

export interface ChatSseMetadataEvent {
  event: 'metadata'
  data: {
    session_id: string
    intent: string
    knowledge_point_ids: string[]
    task_created: boolean
    task_id: string | null
    knowledge_point_names?: Record<string, string>
  }
}

export interface ChatSseDoneEvent {
  event: 'done'
  data: {
    session_id: string
    assistant_message: string
  }
}

export interface ChatSseErrorEvent {
  event: 'error'
  data: {
    message: string
  }
}

export type ChatSseEvent =
  | ChatSseTokenEvent
  | ChatSseMetadataEvent
  | ChatSseDoneEvent
  | ChatSseErrorEvent
