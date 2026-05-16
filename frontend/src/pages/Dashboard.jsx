// src/pages/Dashboard.jsx
import { Cpu, MemoryStick, Network, Activity } from 'lucide-react'
import StatCard from '../components/widgets/StatCard'
import CpuChart from '../components/charts/CpuChart'
import MemoryChart from '../components/charts/MemoryChart'
import NetworkChart from '../components/charts/NetworkChart'
import ProcessTable from '../components/widgets/ProcessTable'
import AlertsPanel from '../components/widgets/AlertsPanel'
import { useWebSocket } from '../hooks/useWebSocket'

const HOSTNAME = 'MacBook-Air-3.local' // your hostname here

export default function Dashboard() {
  const { latest, history } = useWebSocket(HOSTNAME)

  const cpu = latest?.cpu
  const mem = latest?.memory
  const net = latest?.network
  const procs = latest?.processes?.top || []

  return (
    <div className="flex flex-col gap-6 p-6 overflow-y-auto h-full">
      <div>
        <h1 className="text-lg font-semibold text-white">System Overview</h1>
        <p className="text-sm text-gray-500">
          Real-time metrics · WebSocket push · updates every 5s
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="CPU Usage"
          value={cpu?.percent_total?.toFixed(1)}
          unit="%" icon={Cpu} color="blue"
          subtitle={`Load: ${cpu?.load_avg_1m?.toFixed(2)}`}
        />
        <StatCard
          title="RAM Usage"
          value={mem?.ram_percent?.toFixed(1)}
          unit="%" icon={MemoryStick} color="purple"
          subtitle={`${mem?.ram_used_gb?.toFixed(1)} GB used`}
        />
        <StatCard
          title="Net Sent"
          value={net?.bytes_sent_mb?.toFixed(0)}
          unit="MB" icon={Network} color="green"
        />
        <StatCard
          title="Net Recv"
          value={net?.bytes_recv_mb?.toFixed(0)}
          unit="MB" icon={Activity} color="yellow"
        />
      </div>

      {/* Charts — now fed from WebSocket history */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CpuChart data={history.cpu} />
        <MemoryChart data={history.memory} />
      </div>

      <NetworkChart data={history.network} />

      {/* Bottom panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AlertsPanel />
        <ProcessTable processes={procs} />
      </div>
    </div>
  )
}