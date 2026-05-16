// src/components/widgets/AnomalyPanel.jsx
import { useState, useEffect } from 'react'
import { Brain, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { clsx } from 'clsx'

export default function AnomalyPanel({ anomaly }) {
  const [recentAnomalies, setRecentAnomalies] = useState([])

  useEffect(() => {
    if (anomaly?.is_anomaly) {
      setRecentAnomalies(prev => [
        {
          time: new Date().toLocaleTimeString(),
          score: anomaly.score,
          cpu: anomaly.features?.cpu_percent,
          ram: anomaly.features?.ram_percent,
        },
        ...prev.slice(0, 4), // keep last 5
      ])
    }
  }, [anomaly])

  const getStatusInfo = () => {
    if (!anomaly) return { label: 'Connecting...', color: 'gray', icon: Clock }
    if (anomaly.status === 'warming_up') return {
      label: `Warming up — ${anomaly.points_collected}/${anomaly.warmup_required} points`,
      color: 'yellow',
      icon: Clock
    }
    if (anomaly.status === 'training') return {
      label: 'Training model...',
      color: 'yellow',
      icon: Brain
    }
    if (anomaly.is_anomaly) return {
      label: `Anomaly detected! Score: ${anomaly.score}`,
      color: 'red',
      icon: AlertTriangle
    }
    return {
      label: `Normal — score: ${anomaly.score}`,
      color: 'green',
      icon: CheckCircle
    }
  }

  const { label, color, icon: Icon } = getStatusInfo()

  const colors = {
    gray: 'bg-gray-500/10 border-gray-500/20 text-gray-400',
    yellow: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
    red: 'bg-red-500/10 border-red-500/20 text-red-400',
    green: 'bg-green-500/10 border-green-500/20 text-green-400',
  }

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <div className="flex items-center gap-2 mb-4">
        <Brain size={16} className="text-blue-400"/>
        <h3 className="text-sm font-semibold text-gray-300">ML Anomaly Detection</h3>
      </div>

      {/* Current status */}
      <div className={clsx('rounded-lg border p-3 flex items-center gap-3 mb-4', colors[color])}>
        <Icon size={16}/>
        <span className="text-sm font-medium">{label}</span>
      </div>

      {/* Stats row */}
      {anomaly?.total_points > 0 && (
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-gray-800 rounded-lg p-3 text-center">
            <p className="text-lg font-bold text-white">{anomaly.total_points}</p>
            <p className="text-xs text-gray-500">Points seen</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3 text-center">
            <p className="text-lg font-bold text-red-400">{anomaly.anomaly_count ?? 0}</p>
            <p className="text-xs text-gray-500">Anomalies</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3 text-center">
            <p className="text-lg font-bold text-blue-400">
              {anomaly.score !== null ? anomaly.score?.toFixed(3) : '—'}
            </p>
            <p className="text-xs text-gray-500">Score</p>
          </div>
        </div>
      )}

      {/* Recent anomalies list */}
      {recentAnomalies.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2">Recent anomalies</p>
          <div className="flex flex-col gap-1">
            {recentAnomalies.map((a, i) => (
              <div key={i} className="flex items-center justify-between bg-red-500/10 border border-red-500/20 rounded px-3 py-2">
                <span className="text-xs text-gray-400">{a.time}</span>
                <span className="text-xs text-red-400">
                  CPU {a.cpu?.toFixed(1)}% · RAM {a.ram?.toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500">score {a.score}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}