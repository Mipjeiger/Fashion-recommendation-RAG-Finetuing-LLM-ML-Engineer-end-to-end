import { useState } from 'react'
import { useTheme } from '../../store/themeStore'
import { ShoppingCart, Heart } from 'lucide-react'

interface ProductGridProps {
  loading: boolean
  onProductClick: (productId: string) => void
}

// Mock product data - in production, this would come from API
const mockProducts = [
  { id: '1', name: 'Classic White Shirt', price: 49.99, image: '/api/placeholder/300/400' },
  { id: '2', name: 'Slim Fit Jeans', price: 79.99, image: '/api/placeholder/300/400' },
  { id: '3', name: 'Casual Blazer', price: 129.99, image: '/api/placeholder/300/400' },
  { id: '4', name: 'Cotton T-Shirt', price: 29.99, image: '/api/placeholder/300/400' },
  { id: '5', name: 'Formal Trousers', price: 89.99, image: '/api/placeholder/300/400' },
  { id: '6', name: 'Hooded Sweatshirt', price: 59.99, image: '/api/placeholder/300/400' },
]

export default function ProductGrid({ loading, onProductClick }: ProductGridProps) {
  const { theme } = useTheme()
  const [hoveredId, setHoveredId] = useState<string | null>(null)

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className={`animate-pulse rounded-lg ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-gray-200'
            }`}
            style={{ height: '400px' }}
          />
        ))}
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">Featured Products</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockProducts.map((product) => (
          <div
            key={product.id}
            className={`group relative rounded-lg overflow-hidden transition-all duration-300 ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            } shadow-sm hover:shadow-lg`}
            onMouseEnter={() => setHoveredId(product.id)}
            onMouseLeave={() => setHoveredId(null)}
            onClick={() => onProductClick(product.id)}
          >
            {/* Product Image */}
            <div className="aspect-[3/4] bg-gray-200 dark:bg-gray-700 relative overflow-hidden">
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                {product.name}
              </div>
              {hoveredId === product.id && (
                <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center space-x-4 transition-opacity">
                  <button className="p-3 bg-white rounded-full hover:bg-gray-100 transition-colors">
                    <ShoppingCart className="w-5 h-5" />
                  </button>
                  <button className="p-3 bg-white rounded-full hover:bg-gray-100 transition-colors">
                    <Heart className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="p-4">
              <h3 className="font-medium mb-1">{product.name}</h3>
              <p className="text-lg font-semibold">${product.price}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
