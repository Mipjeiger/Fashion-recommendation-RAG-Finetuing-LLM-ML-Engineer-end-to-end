import { useState, useEffect } from 'react'
import { recommendationsApi, RecommendationResponse } from '../api/recommendations'
import ProductGrid from '../components/ecommerce/ProductGrid'
import RecommendationCarousel from '../components/ecommerce/RecommendationCarousel'
import PersonalizationPanel from '../components/ecommerce/PersonalizationPanel'
import { useTheme } from '../store/themeStore'

export default function EcommercePage() {
  const { theme } = useTheme()
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)

  useEffect(() => {
    // Load initial recommendations
    loadRecommendations()
    
    // Poll for updates every 5 seconds
    const interval = setInterval(() => {
      if (sessionId) {
        loadRecommendations(sessionId)
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [sessionId])

  const loadRecommendations = async (existingSessionId?: string) => {
    try {
      setLoading(true)
      const response = await recommendationsApi.getRecommendations({
        user_id: 'user_123',
        session_id: existingSessionId || undefined,
      })
      setRecommendations(response)
      if (!existingSessionId) {
        setSessionId(response.session_id)
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProductClick = async (productId: string) => {
    try {
      await recommendationsApi.getRecommendations({
        user_id: 'user_123',
        session_id: sessionId || undefined,
        product_id: productId,
      })
      // Reload recommendations after click
      loadRecommendations(sessionId || undefined)
    } catch (error) {
      console.error('Failed to update recommendations:', error)
    }
  }

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-4">Discover Your Style</h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            AI-powered fashion recommendations tailored just for you
          </p>
        </div>

        {/* Recommendation Carousel */}
        {recommendations && (
          <div className="mb-12">
            <RecommendationCarousel
              recommendations={recommendations.recommendations}
              onProductClick={handleProductClick}
            />
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Product Grid */}
          <div className="lg:col-span-3">
            <ProductGrid
              loading={loading}
              onProductClick={handleProductClick}
            />
          </div>

          {/* Personalization Panel */}
          <div className="lg:col-span-1">
            <PersonalizationPanel
              recommendations={recommendations}
              loading={loading}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
