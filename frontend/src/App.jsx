import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import { useWebSocket } from './hooks/useWebSocket'

export default function App() {
  const [hostname, setHostname] = useState('')

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/metrics/hosts')
      .then(r => r.json())
      .then(data => {
        if (data.hosts?.length > 0) setHostname(data.hosts[0])
      })
      .catch(() => {})
    const interval = setInterval(() => {
      fetch('http://localhost:8000/api/v1/metrics/hosts')
        .then(r => r.json())
        .then(data => {
          if (data.hosts?.length > 0) setHostname(data.hosts[0])
        })
        .catch(() => {})
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const { connected } = useWebSocket(hostname)

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
        <Sidebar/>
        <div className="flex flex-col flex-1 overflow-hidden">
          <Header hostname={hostname || 'Connecting...'} connected={connected}/>
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<Dashboard hostname={hostname}/>}/>
              <Route path="/alerts" element={<Alerts/>}/>
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}