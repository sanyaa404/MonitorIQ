// src/components/charts/NetworkChart.jsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { useMetrics } from '../../hooks/useMetrics'

export default function NetworkChart({ hostname }) {
  const { data, loading } = useMetrics('network', hostname, 30)

  if (loading && data.length === 0) return (
    <div className="h-64 flex items-center justify-center text-gray-500 text-sm">
      Loading network data...
    </div>
  )

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Network Traffic (MB)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937"/>
          <XAxis dataKey="time" tick={{ fill: '#6b7280', fontSize: 11 }} interval="preserveStartEnd"/>
          <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} unit=" MB"/>
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 8 }}
            labelStyle={{ color: '#9ca3af' }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }}/>
          <Line type="monotone" dataKey="bytes_sent_mb" stroke="#10b981" strokeWidth={2} dot={false} name="Sent MB"/>
          <Line type="monotone" dataKey="bytes_recv_mb" stroke="#f59e0b" strokeWidth={2} dot={false} name="Recv MB"/>
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}