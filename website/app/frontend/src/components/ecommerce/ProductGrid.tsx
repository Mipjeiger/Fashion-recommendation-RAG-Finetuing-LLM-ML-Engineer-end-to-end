import { useState, useEffect } from 'react'
import { useTheme } from '../../store/themeStore'
import { ShoppingCart, Heart } from 'lucide-react'
import axios from 'axios'

interface ProductGridProps {
  loading: boolean
  onProductClick: (productId: string) => void
}

interface Product {
  id: string
  name: string
  price: number
  image: string
}

export default function ProductGrid({ loading: initialLoading, onProductClick }: ProductGridProps) {
  const { theme } = useTheme()
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(initialLoading)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true)
        const response = await axios.get('/api/v1/products')
        setProducts(response.data)
      } catch (error) {
        console.error('Error fetching products:', error)
      } finally {
        setLoading(false)
      }
    }

    if (!initialLoading) {
      fetchProducts()
    }
  }, [initialLoading])

  if (loading || initialLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className={`animate-pulse rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-200'
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
        {products.map((product) => (
          <div
            key={product.id}
            className={`group relative rounded-lg overflow-hidden transition-all duration-300 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'
              } shadow-sm hover:shadow-lg`}
            onMouseEnter={() => setHoveredId(product.id)}
            onMouseLeave={() => setHoveredId(null)}
            onClick={() => onProductClick(product.id)}
          >
            {/* Product Image */}
            <div className="aspect-[3/4] bg-gray-200 dark:bg-gray-700 relative overflow-hidden">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/api/placeholder/300/400'
                }}
              />
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
              <h3 className="font-medium mb-1 line-clamp-2" title={product.name}>{product.name}</h3>
              <p className="text-lg font-semibold">${product.price}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
