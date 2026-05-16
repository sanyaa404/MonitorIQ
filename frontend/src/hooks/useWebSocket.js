// src/hooks/useWebSocket.js
import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = 'ws://localhost:8000/ws/metrics'
const MAX_HISTORY = 60 // keep last 60 data points per metric

export function useWebSocket(hostname) {
  const [connected, setConnected] = useState(false)
  const [latest, setLatest] = useState(null)
  const [history, setHistory] = useState({
    cpu: [],
    memory: [],
    network: [],
  })
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const addToHistory = useCallback((type, point) => {
    setHistory(prev => ({
      ...prev,
      [type]: [...prev[type].slice(-(MAX_HISTORY - 1)), point],
    }))
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      console.log('[WS] Connected')
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current)
        reconnectTimer.current = null
      }
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (!hostname || data.hostname !== hostname) return

        const time = new Date(data.timestamp).toLocaleTimeString()

        setLatest(data)

        // Add to rolling history for charts
        addToHistory('cpu', {
          time,
          percent_total: data.cpu.percent_total,
          load_avg_1m: data.cpu.load_avg_1m,
        })

        addToHistory('memory', {
          time,
          ram_percent: data.memory.ram_percent,
          swap_percent: data.memory.swap_percent,
        })

        addToHistory('network', {
          time,
          bytes_sent_mb: data.network.bytes_sent_mb,
          bytes_recv_mb: data.network.bytes_recv_mb,
        })

      } catch (e) {
        console.error('[WS] Parse error:', e)
      }
    }

    ws.onclose = () => {
      setConnected(false)
      console.log('[WS] Disconnected — reconnecting in 3s')
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = (e) => {
      console.error('[WS] Error:', e)
      ws.close()
    }
  }, [hostname, addToHistory])

  useEffect(() => {
    connect()
    return () => {
      if (wsRef.current) wsRef.current.close()
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
    }
  }, [connect])

  return { connected, latest, history }
}