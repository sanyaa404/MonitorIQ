// src/components/widgets/StatCard.jsx
import { clsx } from 'clsx'

export default function StatCard({ title, value, unit, icon: Icon, color, subtitle }) {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    green: 'bg-green-500/10 text-green-400 border-green-500/20',
    yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    red: 'bg-red-500/10 text-red-400 border-red-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  }

  return (
    <div className={clsx(
      'rounded-xl border p-5 flex flex-col gap-3',
      colors[color] || colors.blue
    )}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium opacity-70">{title}</span>
        {Icon && <Icon size={18} className="opacity-60" />}
      </div>
      <div className="flex items-end gap-1">
        <span className="text-3xl font-bold">{value ?? '—'}</span>
        {unit && <span className="text-sm opacity-60 mb-1">{unit}</span>}
      </div>
      {subtitle && <p className="text-xs opacity-50">{subtitle}</p>}
    </div>
  )
}