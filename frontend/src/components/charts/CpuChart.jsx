// src/components/charts/CpuChart.jsx
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts'

export default function CpuChart({ data = [] }) {
  if (data.length === 0) return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">CPU Usage %</h3>
      <div className="h-52 flex items-center justify-center text-gray-500 text-sm">
        Waiting for data...
      </div>
    </div>
  )

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">CPU Usage %</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937"/>
          <XAxis dataKey="time" tick={{ fill: '#6b7280', fontSize: 11 }} interval="preserveStartEnd"/>
          <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} unit="%"/>
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 8 }}
            labelStyle={{ color: '#9ca3af' }}
            itemStyle={{ color: '#3b82f6' }}
          />
          <Area
            type="monotone"
            dataKey="percent_total"
            stroke="#3b82f6"
            fill="url(#cpuGrad)"
            strokeWidth={2}
            dot={false}
            name="CPU %"
            isAnimated={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}