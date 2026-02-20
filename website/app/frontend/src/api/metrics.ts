import { apiClient } from './client'

export interface KPISummary {
  ai_revenue_share: string
  avg_cart_uplift: string
  top_behavior_discovery: string
}

export const metricsApi = {
  getKPI: async (): Promise<KPISummary> => {
    const response = await apiClient.get('/metrics/kpi')
    return response.data.data
  },
  
  getDailyMetrics: async (date?: string) => {
    const response = await apiClient.post('/metrics/daily', { date })
    return response.data
  },
  
  getWeeklyInsights: async () => {
    const response = await apiClient.post('/metrics/weekly')
    return response.data
  },
}
