import apiClient from './apiClient'
import type { DiagnosisReport, SaveSimplifiedDiagnosisReportPayload } from '../types/api'

export const diagnosisService = {
  async saveSimplifiedReport(payload: SaveSimplifiedDiagnosisReportPayload): Promise<DiagnosisReport> {
    const response = await apiClient.post<DiagnosisReport>('/diagnosis-reports/simplified', payload)
    return response.data
  },

  async bindGeneratedPlan(reportId: string, generatedPlanId: string): Promise<DiagnosisReport> {
    const response = await apiClient.put<DiagnosisReport>(`/diagnosis-reports/${reportId}/generated-plan`, {
      generated_plan_id: generatedPlanId,
    })
    return response.data
  },
}
