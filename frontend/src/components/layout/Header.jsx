// src/components/layout/Header.jsx
import { Wifi, WifiOff } from 'lucide-react'

export default function Header({ hostname, connected }) {
  return (
    <header className="h-14 bg-gray-950 border-b border-gray-800 flex items-center justify-between px-6">
      <div>
        <span className="text-sm text-gray-400">Monitoring </span>
        <span className="text-sm font-mono text-white">{hostname}</span>
      </div>
      <div className="flex items-center gap-2">
        {connected ? (
          <><Wifi size={14} className="text-green-400"/><span className="text-xs text-green-400">Live</span></>
        ) : (
          <><WifiOff size={14} className="text-red-400"/><span className="text-xs text-red-400">Offline</span></>
        )}
      </div>
    </header>
  )
}