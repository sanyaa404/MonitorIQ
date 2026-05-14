// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import { useWebSocket } from './hooks/useWebSocket'

const HOSTNAME = 'MacBook-Air-3.local'

export default function App() {
  const { connected } = useWebSocket(HOSTNAME)

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
        <Sidebar/>
        <div className="flex flex-col flex-1 overflow-hidden">
          <Header hostname={HOSTNAME} connected={connected}/>
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<Dashboard/>}/>
              <Route path="/alerts" element={<Alerts/>}/>
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}