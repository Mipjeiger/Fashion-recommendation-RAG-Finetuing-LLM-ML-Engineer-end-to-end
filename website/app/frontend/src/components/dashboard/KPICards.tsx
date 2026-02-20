import { KPISummary } from '../../api/metrics'
import { useTheme } from '../../store/themeStore'
import { DollarSign, TrendingUp, Lightbulb } from 'lucide-react'

interface KPICardsProps {
  kpi: KPISummary | null
  loading: boolean
}

export default function KPICards({ kpi, loading }: KPICardsProps) {
  const { theme } = useTheme()

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className={`animate-pulse rounded-lg ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}
            style={{ height: '120px' }}
          />
        ))}
      </div>
    )
  }

  const cards = [
    {
      title: 'AI Revenue Share',
      value: kpi?.ai_revenue_share || '0%',
      icon: DollarSign,
      color: 'text-green-600 dark:text-green-400',
    },
    {
      title: 'Avg Cart Uplift',
      value: kpi?.avg_cart_uplift || '$0',
      icon: TrendingUp,
      color: 'text-blue-600 dark:text-blue-400',
    },
    {
      title: 'Top Discovery',
      value: kpi?.top_behavior_discovery?.substring(0, 50) + '...' || 'No data',
      icon: Lightbulb,
      color: 'text-purple-600 dark:text-purple-400',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon
        return (
          <div
            key={index}
            className={`rounded-lg p-6 shadow-sm ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {card.title}
              </h3>
              <Icon className={`w-5 h-5 ${card.color}`} />
            </div>
            <p className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              {card.value}
            </p>
          </div>
        )
      })}
    </div>
  )
}
