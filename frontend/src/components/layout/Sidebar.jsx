// src/components/layout/Sidebar.jsx
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Bell, Activity } from 'lucide-react'
import { clsx } from 'clsx'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-gray-950 border-r border-gray-800 flex flex-col">
      <div className="p-5 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Activity size={20} className="text-blue-400"/>
          <span className="font-bold text-white text-sm">MonitorIQ</span>
        </div>
      </div>
      <nav className="flex flex-col gap-1 p-3 flex-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
              isActive
                ? 'bg-blue-500/10 text-blue-400 font-medium'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            )}
          >
            <Icon size={16}/>
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-800">
        <p className="text-xs text-gray-600">v1.0.0 · Layer 1</p>
      </div>
    </aside>
  )
}