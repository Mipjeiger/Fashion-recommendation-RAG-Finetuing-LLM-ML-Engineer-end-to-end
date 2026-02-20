import { useTheme } from '../../store/themeStore'
import { AlertTriangle, CheckCircle } from 'lucide-react'

export default function DriftPanel() {
  const { theme } = useTheme()

  // Mock drift status - in production, this would come from API
  const driftStatus = {
    detected: false,
    score: 0.08,
    threshold: 0.15,
    lastCheck: '2026-02-20 14:30:00',
  }

  return (
    <div className={`rounded-lg p-6 shadow-sm ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Drift Detection</h3>
        {driftStatus.detected ? (
          <AlertTriangle className="w-5 h-5 text-red-500" />
        ) : (
          <CheckCircle className="w-5 h-5 text-green-500" />
        )}
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-600 dark:text-gray-400">Drift Score</span>
            <span className="font-medium">
              {(driftStatus.score * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                driftStatus.detected ? 'bg-red-500' : 'bg-green-500'
              }`}
              style={{ width: `${(driftStatus.score / driftStatus.threshold) * 100}%` }}
            />
          </div>
        </div>

        <div className="text-sm">
          <p className="text-gray-600 dark:text-gray-400">
            Threshold: {(driftStatus.threshold * 100).toFixed(0)}%
          </p>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Last Check: {driftStatus.lastCheck}
          </p>
        </div>

        {driftStatus.detected && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <p className="text-sm text-red-800 dark:text-red-200">
              Drift detected! Model may need retraining.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
