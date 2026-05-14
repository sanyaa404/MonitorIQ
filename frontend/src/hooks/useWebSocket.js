// src/hooks/useWebSocket.js
import { useState, useEffect, useRef } from 'react'

export function useWebSocket(hostname) {
  const [latest, setLatest] = useState(null)
  const [connected, setConnected] = useState(false)
  const intervalRef = useRef(null)

  useEffect(() => {
    if (!hostname) return

    // Poll every 5s as WebSocket bridge (we add true WS in Layer 2)
    const fetchLatest = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/v1/metrics/query/cpu?host=${hostname}&minutes=1`
        )
        const data = await res.json()
        if (data.data && data.data.length > 0) {
          setLatest(data)
          setConnected(true)
        }
      } catch {
        setConnected(false)
      }
    }

    fetchLatest()
    intervalRef.current = setInterval(fetchLatest, 5000)
    return () => clearInterval(intervalRef.current)
  }, [hostname])

  return { latest, connected }
}