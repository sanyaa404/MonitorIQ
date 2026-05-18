import { Cpu, MemoryStick, Network, Activity } from 'lucide-react'
import StatCard from '../components/widgets/StatCard'
import CpuChart from '../components/charts/CpuChart'
import MemoryChart from '../components/charts/MemoryChart'
import NetworkChart from '../components/charts/NetworkChart'
import ProcessTable from '../components/widgets/ProcessTable'
import AlertsPanel from '../components/widgets/AlertsPanel'
import AnomalyPanel from '../components/widgets/AnomalyPanel'
import { useWebSocket } from '../hooks/useWebSocket'

export default function Dashboard({ hostname }) {
  const { latest, history } = useWebSocket(hostname)

  const cpu = latest?.cpu
  const mem = latest?.memory
  const net = latest?.network
  const procs = latest?.processes?.top || []
  const anomaly = latest?.anomaly

  return (
    <div className="flex flex-col gap-6 p-6 overflow-y-auto h-full">
      <div>
        <h1 className="text-lg font-semibold text-white">System Overview</h1>
        <p className="text-sm text-gray-500">
          Real-time metrics · WebSocket push · ML anomaly detection
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="CPU Usage" value={cpu?.percent_total?.toFixed(1)} unit="%" icon={Cpu} color="blue" subtitle={`Load: ${cpu?.load_avg_1m?.toFixed(2)}`}/>
        <StatCard title="RAM Usage" value={mem?.ram_percent?.toFixed(1)} unit="%" icon={MemoryStick} color="purple" subtitle={`${mem?.ram_used_gb?.toFixed(1)} GB used`}/>
        <StatCard title="Net Sent" value={net?.bytes_sent_mb?.toFixed(0)} unit="MB" icon={Network} color="green"/>
        <StatCard title="Net Recv" value={net?.bytes_recv_mb?.toFixed(0)} unit="MB" icon={Activity} color="yellow"/>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CpuChart data={history.cpu}/>
        <MemoryChart data={history.memory}/>
      </div>

      <NetworkChart data={history.network}/>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AnomalyPanel anomaly={anomaly}/>
        <AlertsPanel/>
      </div>

      <ProcessTable processes={procs}/>
    </div>
  )
}