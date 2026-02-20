import { useTheme } from '../../store/themeStore'
import { Package } from 'lucide-react'

export default function ModelVersion() {
  const { theme } = useTheme()

  // Mock model info - in production, this would come from API
  const modelInfo = {
    version: 'v1.2.3',
    lastReload: '2026-02-20 10:15:00',
    models: ['tensorflow_recommender', 'pytorch_reranker'],
    status: 'loaded',
  }

  return (
    <div className={`rounded-lg p-6 shadow-sm ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}>
      <div className="flex items-center space-x-2 mb-4">
        <Package className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Model Registry</h3>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">Version</p>
          <p className="text-lg font-semibold">{modelInfo.version}</p>
        </div>

        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
          <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
            modelInfo.status === 'loaded'
              ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
          }`}>
            {modelInfo.status.toUpperCase()}
          </span>
        </div>

        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Loaded Models</p>
          <div className="space-y-1">
            {modelInfo.models.map((model) => (
              <div key={model} className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                {model}
              </div>
            ))}
          </div>
        </div>

        <div className="text-xs text-gray-500 dark:text-gray-400 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          Last Reload: {modelInfo.lastReload}
        </div>
      </div>
    </div>
  )
}
