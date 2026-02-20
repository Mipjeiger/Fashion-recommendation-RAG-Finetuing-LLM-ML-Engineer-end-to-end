import { apiClient } from './client'

export interface RecommendationRequest {
  user_id?: string
  session_id?: string
  product_id?: string
  context?: Record<string, any>
}

export interface RecommendationResponse {
  status: string
  session_id: string
  recommendations: {
    session_id: string
    user_id: string
    models: {
      tensorflow_recommender: {
        intent_score: number
        predicted_intent: string
      }
      pytorch_reranker: {
        ranking_confidence: number
      }
    }
    rag_assessment: {
      summary: string
      recommendation_reason: string
    }
    business_impact: {
      real_time_adaptation: {
        enabled: boolean
      }
    }
    system_metadata: {
      latency_ms: number
    }
  }
}

export const recommendationsApi = {
  getRecommendations: async (request: RecommendationRequest): Promise<RecommendationResponse> => {
    const response = await apiClient.post('/recommendations/recommend', request)
    return response.data
  },
  
  logClick: async (recommendationId: string) => {
    const response = await apiClient.post(`/recommendations/click?recommendation_id=${recommendationId}`)
    return response.data
  },
  
  logPurchase: async (recommendationId: string) => {
    const response = await apiClient.post(`/recommendations/purchase?recommendation_id=${recommendationId}`)
    return response.data
  },
}
