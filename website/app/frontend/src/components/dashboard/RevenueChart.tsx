import { useTheme } from '../../store/themeStore'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

// Mock data - in production, this would come from API
const mockData = [
  { date: 'Mon', revenue: 12000, aiRevenue: 2640 },
  { date: 'Tue', revenue: 15000, aiRevenue: 3300 },
  { date: 'Wed', revenue: 18000, aiRevenue: 3960 },
  { date: 'Thu', revenue: 14000, aiRevenue: 3080 },
  { date: 'Fri', revenue: 20000, aiRevenue: 4400 },
  { date: 'Sat', revenue: 25000, aiRevenue: 5500 },
  { date: 'Sun', revenue: 22000, aiRevenue: 4840 },
]

export default function RevenueChart() {
  const { theme } = useTheme()
  const textColor = theme === 'dark' ? '#e5e7eb' : '#374151'
  const gridColor = theme === 'dark' ? '#374151' : '#e5e7eb'

  return (
    <div className={`rounded-lg p-6 shadow-sm ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}>
      <h3 className="text-lg font-semibold mb-4">Revenue Trends</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={mockData}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis dataKey="date" stroke={textColor} />
          <YAxis stroke={textColor} />
          <Tooltip
            contentStyle={{
              backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
              border: `1px solid ${gridColor}`,
              color: textColor,
            }}
          />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Total Revenue"
          />
          <Line
            type="monotone"
            dataKey="aiRevenue"
            stroke="#10b981"
            strokeWidth={2}
            name="AI-Driven Revenue"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
