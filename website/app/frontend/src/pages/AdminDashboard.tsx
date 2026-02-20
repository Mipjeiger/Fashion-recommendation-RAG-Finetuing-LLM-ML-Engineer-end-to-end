import { useState, useEffect } from 'react'
import { metricsApi, KPISummary } from '../api/metrics'
import KPICards from '../components/dashboard/KPICards'
import RevenueChart from '../components/dashboard/RevenueChart'
import DriftPanel from '../components/dashboard/DriftPanel'
import KafkaMonitor from '../components/dashboard/KafkaMonitor'
import SlackPreview from '../components/dashboard/SlackPreview'
import ModelVersion from '../components/dashboard/ModelVersion'
import { useTheme } from '../store/themeStore'

export default function AdminDashboard() {
  const { theme } = useTheme()
  const [kpi, setKpi] = useState<KPISummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadKPIs()
    const interval = setInterval(loadKPIs, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const loadKPIs = async () => {
    try {
      const data = await metricsApi.getKPI()
      setKpi(data)
    } catch (error) {
      console.error('Failed to load KPIs:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time insights and monitoring for IndoCloth Market
          </p>
        </div>

        {/* KPI Cards */}
        <KPICards kpi={kpi} loading={loading} />

        {/* Charts and Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <RevenueChart />
          <DriftPanel />
        </div>

        {/* Monitoring Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          <KafkaMonitor />
          <SlackPreview />
          <ModelVersion />
        </div>
      </div>
    </div>
  )
}
