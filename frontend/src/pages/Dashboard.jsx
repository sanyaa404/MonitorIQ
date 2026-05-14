// src/pages/Dashboard.jsx
import { useState, useEffect } from 'react'
import { Cpu, MemoryStick, Network, Activity } from 'lucide-react'
import StatCard from '../components/widgets/StatCard'
import CpuChart from '../components/charts/CpuChart'
import MemoryChart from '../components/charts/MemoryChart'
import NetworkChart from '../components/charts/NetworkChart'
import ProcessTable from '../components/widgets/ProcessTable'
import AlertsPanel from '../components/widgets/AlertsPanel'
import { metricsApi } from '../services/api'

const HOSTNAME = 'MacBook-Air-3.local' 

export default function Dashboard() {
  const [snapshot, setSnapshot] = useState(null)

  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        const [cpu, mem, net] = await Promise.all([
          metricsApi.query('cpu', HOSTNAME, 1),
          metricsApi.query('memory', HOSTNAME, 1),
          metricsApi.query('network', HOSTNAME, 1),
        ])
        const latest = (arr) => arr.data[arr.data.length - 1]?.value
        const field = (arr, f) => arr.data.filter(d => d.field === f).slice(-1)[0]?.value
        setSnapshot({
          cpu: field(cpu, 'percent_total'),
          ram: field(mem, 'ram_percent'),
          sent: field(net, 'bytes_sent_mb'),
          recv: field(net, 'bytes_recv_mb'),
        })
      } catch {}
    }
    fetchSnapshot()
    const i = setInterval(fetchSnapshot, 5000)
    return () => clearInterval(i)
  }, [])

  return (
    <div className="flex flex-col gap-6 p-6 overflow-y-auto h-full">
      <div>
        <h1 className="text-lg font-semibold text-white">System Overview</h1>
        <p className="text-sm text-gray-500">Real-time metrics · updates every 5s</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="CPU Usage" value={snapshot?.cpu?.toFixed(1)} unit="%" icon={Cpu} color="blue"/>
        <StatCard title="RAM Usage" value={snapshot?.ram?.toFixed(1)} unit="%" icon={MemoryStick} color="purple"/>
        <StatCard title="Net Sent" value={snapshot?.sent?.toFixed(0)} unit="MB" icon={Network} color="green"/>
        <StatCard title="Net Recv" value={snapshot?.recv?.toFixed(0)} unit="MB" icon={Activity} color="yellow"/>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CpuChart hostname={HOSTNAME}/>
        <MemoryChart hostname={HOSTNAME}/>
      </div>

      <NetworkChart hostname={HOSTNAME}/>

      {/* Bottom panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AlertsPanel/>
        <ProcessTable processes={[]}/>
      </div>
    </div>
  )
}