import { useTheme } from '../../store/themeStore'
import { Activity } from 'lucide-react'

export default function KafkaMonitor() {
  const { theme } = useTheme()

  // Mock Kafka status - in production, this would come from API
  const kafkaStatus = {
    healthy: true,
    topics: ['realtime-recommendations', 'fashion-events'],
    messagesPerSecond: 42,
    consumerLag: 0,
  }

  return (
    <div className={`rounded-lg p-6 shadow-sm ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}>
      <div className="flex items-center space-x-2 mb-4">
        <Activity className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Kafka Stream</h3>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">Status</span>
          <span className={`text-sm font-medium ${
            kafkaStatus.healthy ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {kafkaStatus.healthy ? 'Healthy' : 'Unhealthy'}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">Messages/sec</span>
          <span className="text-sm font-medium">{kafkaStatus.messagesPerSecond}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">Consumer Lag</span>
          <span className="text-sm font-medium">{kafkaStatus.consumerLag}</span>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">Active Topics</p>
          <div className="space-y-1">
            {kafkaStatus.topics.map((topic) => (
              <div key={topic} className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                {topic}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
