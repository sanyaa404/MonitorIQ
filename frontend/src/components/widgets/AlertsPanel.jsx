// src/components/widgets/AlertsPanel.jsx
import { useState, useEffect } from 'react'
import { alertsApi } from '../../services/api'
import { Bell, CheckCircle } from 'lucide-react'

export default function AlertsPanel() {
  const [events, setEvents] = useState([])

  const load = async () => {
    try {
      const data = await alertsApi.getEvents()
      setEvents(data)
    } catch {}
  }

  const ack = async (id) => {
    await alertsApi.acknowledge(id)
    load()
  }

  useEffect(() => { load(); const i = setInterval(load, 10000); return () => clearInterval(i) }, [])

  const unacked = events.filter(e => !e.acknowledged)

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-300">Active Alerts</h3>
        {unacked.length > 0 && (
          <span className="bg-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded-full">
            {unacked.length} active
          </span>
        )}
      </div>
      {unacked.length === 0 ? (
        <div className="flex items-center gap-2 text-green-400 text-sm">
          <CheckCircle size={16}/> All clear
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {unacked.slice(0, 5).map(e => (
            <div key={e.id} className="flex items-center justify-between bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              <div>
                <p className="text-sm font-medium text-red-400">{e.rule_name}</p>
                <p className="text-xs text-gray-500">{e.metric} = {e.value.toFixed(2)} on {e.hostname}</p>
              </div>
              <button
                onClick={() => ack(e.id)}
                className="text-xs text-gray-400 hover:text-white border border-gray-700 rounded px-2 py-1"
              >
                Ack
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}