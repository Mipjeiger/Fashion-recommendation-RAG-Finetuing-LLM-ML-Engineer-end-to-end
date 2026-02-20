import { useTheme } from '../../store/themeStore'
import { Sparkles, TrendingUp } from 'lucide-react'

interface PersonalizationPanelProps {
  recommendations: any
  loading: boolean
}

export default function PersonalizationPanel({
  recommendations,
  loading,
}: PersonalizationPanelProps) {
  const { theme } = useTheme()

  if (loading) {
    return (
      <div className={`rounded-lg p-6 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4" />
          <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2" />
        </div>
      </div>
    )
  }

  const aiImpact = recommendations?.business_impact?.real_time_adaptation?.enabled
    ? 'Active'
    : 'Inactive'

  return (
    <div className={`rounded-lg p-6 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} shadow-sm sticky top-8`}>
      <div className="flex items-center space-x-2 mb-4">
        <Sparkles className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Your Style Profile</h3>
      </div>

      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">AI Personalization</p>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              aiImpact === 'Active' ? 'bg-green-500' : 'bg-gray-400'
            }`} />
            <span className="text-sm font-medium">{aiImpact}</span>
          </div>
        </div>

        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Session Activity</p>
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <span className="text-sm">Analyzing your preferences...</span>
          </div>
        </div>

        {recommendations?.rag_assessment?.summary && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">AI Insight</p>
            <p className="text-sm">{recommendations.rag_assessment.summary.substring(0, 150)}...</p>
          </div>
        )}
      </div>
    </div>
  )
}
