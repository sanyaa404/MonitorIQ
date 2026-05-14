// src/pages/Alerts.jsx
import { useState, useEffect } from 'react'
import { alertsApi } from '../services/api'
import { Bell, Plus } from 'lucide-react'

export default function Alerts() {
  const [rules, setRules] = useState([])
  const [events, setEvents] = useState([])
  const [form, setForm] = useState({ name: '', metric: 'cpu_percent_total', operator: 'gt', threshold: 80, hostname: '' })

  const load = async () => {
    try {
      const [r, e] = await Promise.all([alertsApi.getRules(), alertsApi.getEvents()])
      setRules(r); setEvents(e)
    } catch {}
  }

  const submit = async () => {
    await alertsApi.createRule({ ...form, threshold: parseFloat(form.threshold) })
    load()
  }

  useEffect(() => { load() }, [])

  return (
    <div className="flex flex-col gap-6 p-6 overflow-y-auto h-full">
      <h1 className="text-lg font-semibold text-white">Alert Management</h1>

      {/* Create rule */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
          <Plus size={14}/> Create Alert Rule
        </h3>
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
          <input
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white"
            placeholder="Rule name"
            value={form.name}
            onChange={e => setForm(f => ({...f, name: e.target.value}))}
          />
          <select
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white"
            value={form.metric}
            onChange={e => setForm(f => ({...f, metric: e.target.value}))}
          >
            <option value="cpu_percent_total">CPU %</option>
            <option value="ram_percent">RAM %</option>
            <option value="swap_percent">Swap %</option>
            <option value="load_avg_1m">Load Avg 1m</option>
          </select>
          <select
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white"
            value={form.operator}
            onChange={e => setForm(f => ({...f, operator: e.target.value}))}
          >
            <option value="gt">Greater than</option>
            <option value="lt">Less than</option>
            <option value="gte">≥</option>
            <option value="lte">≤</option>
          </select>
          <input
            type="number"
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white"
            placeholder="Threshold"
            value={form.threshold}
            onChange={e => setForm(f => ({...f, threshold: e.target.value}))}
          />
          <button
            onClick={submit}
            className="bg-blue-600 hover:bg-blue-500 text-white rounded-lg px-4 py-2 text-sm font-medium"
          >
            Create
          </button>
        </div>
      </div>

      {/* Rules list */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Active Rules</h3>
        {rules.length === 0 ? (
          <p className="text-gray-500 text-sm">No rules yet. Create one above.</p>
        ) : rules.map(r => (
          <div key={r.id} className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
            <span className="text-sm text-white">{r.name}</span>
            <span className="text-xs text-gray-400 font-mono">{r.metric} {r.operator} {r.threshold}</span>
          </div>
        ))}
      </div>

      {/* Recent events */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Recent Alert Events</h3>
        {events.length === 0 ? (
          <p className="text-gray-500 text-sm">No alerts fired yet.</p>
        ) : events.slice(0, 10).map(e => (
          <div key={e.id} className={`flex items-center justify-between py-2 border-b border-gray-800 last:border-0 ${e.acknowledged ? 'opacity-40' : ''}`}>
            <div>
              <p className="text-sm text-red-400">{e.rule_name}</p>
              <p className="text-xs text-gray-500">{e.metric} = {e.value.toFixed(2)} on {e.hostname}</p>
            </div>
            <span className="text-xs text-gray-500">{new Date(e.fired_at).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}