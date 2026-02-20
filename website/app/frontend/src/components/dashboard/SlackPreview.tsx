import { useTheme } from '../../store/themeStore'
import { MessageSquare } from 'lucide-react'

export default function SlackPreview() {
  const { theme } = useTheme()

  // Mock Slack notifications - in production, this would come from API
  const recentNotifications = [
    { type: 'daily_report', message: 'Daily AI Revenue Report sent', time: '2 hours ago' },
    { type: 'drift_detected', message: 'Data drift detected', time: '5 hours ago' },
    { type: 'model_deployed', message: 'New model version deployed', time: '1 day ago' },
  ]

  return (
    <div className={`rounded-lg p-6 shadow-sm ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}>
      <div className="flex items-center space-x-2 mb-4">
        <MessageSquare className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Slack Events</h3>
      </div>

      <div className="space-y-3">
        {recentNotifications.map((notif, index) => (
          <div
            key={index}
            className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium">{notif.message}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {notif.time}
                </p>
              </div>
              <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                {notif.type.replace('_', ' ')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
