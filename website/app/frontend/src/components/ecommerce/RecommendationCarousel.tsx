import { useTheme } from '../../store/themeStore'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useState } from 'react'

interface RecommendationCarouselProps {
  recommendations: any
  onProductClick: (productId: string) => void
}

export default function RecommendationCarousel({
  recommendations,
  onProductClick,
}: RecommendationCarouselProps) {
  const { theme } = useTheme()
  const [currentIndex, setCurrentIndex] = useState(0)

  const intentScore = recommendations?.models?.tensorflow_recommender?.intent_score || 0
  const intentLabel = recommendations?.models?.tensorflow_recommender?.predicted_intent || 'exploring'
  const reason = recommendations?.rag_assessment?.recommendation_reason || ''

  const mockRecommendedProducts = [
    { id: 'rec1', name: 'Recommended Item 1', price: 59.99 },
    { id: 'rec2', name: 'Recommended Item 2', price: 69.99 },
    { id: 'rec3', name: 'Recommended Item 3', price: 79.99 },
  ]

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % mockRecommendedProducts.length)
  }

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + mockRecommendedProducts.length) % mockRecommendedProducts.length)
  }

  return (
    <div className={`rounded-lg p-6 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">AI Recommendations for You</h2>
          <div className="flex items-center space-x-4 text-sm">
            <span className={`px-3 py-1 rounded-full ${
              intentLabel === 'purchase_ready' 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
            }`}>
              {intentLabel.replace('_', ' ').toUpperCase()}
            </span>
            <span className="text-gray-600 dark:text-gray-400">
              Confidence: {(intentScore * 100).toFixed(0)}%
            </span>
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={prevSlide}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={nextSlide}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {reason && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{reason}</p>
      )}

      <div className="relative">
        <div className="flex space-x-4 overflow-hidden">
          {mockRecommendedProducts.map((product, index) => (
            <div
              key={product.id}
              className={`flex-shrink-0 w-64 rounded-lg overflow-hidden transition-transform duration-300 ${
                theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'
              } ${index === currentIndex ? 'scale-105' : ''}`}
              style={{ transform: `translateX(-${currentIndex * 100}%)` }}
            >
              <div className="aspect-[3/4] bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                {product.name}
              </div>
              <div className="p-4">
                <h3 className="font-medium mb-1">{product.name}</h3>
                <p className="text-lg font-semibold">${product.price}</p>
                <button
                  onClick={() => onProductClick(product.id)}
                  className="mt-2 w-full py-2 bg-black dark:bg-white text-white dark:text-black rounded hover:opacity-90 transition-opacity"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
