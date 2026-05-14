// src/hooks/useMetrics.js
import { useState, useEffect, useCallback } from 'react'
import { metricsApi } from '../services/api'

export function useMetrics(measurement, hostname, minutes = 30) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    if (!hostname) return
    try {
      setLoading(true)
      const res = await metricsApi.query(measurement, hostname, minutes)
      
      // Debug — remove after fixing
      console.log(`[${measurement}] raw response:`, res)
      console.log(`[${measurement}] data points:`, res.data?.length)
      if (res.data?.length > 0) console.log(`[${measurement}] sample point:`, res.data[0])

      const grouped = {}
      res.data.forEach(point => {
        const time = new Date(point.time).toLocaleTimeString()
        if (!grouped[time]) grouped[time] = { time }
        grouped[time][point.field] = parseFloat(point.value?.toFixed(2))
      })
      const result = Object.values(grouped)
      console.log(`[${measurement}] grouped result:`, result.length, 'points')
      setData(result)
      setError(null)
    } catch (e) {
      console.error(`[${measurement}] error:`, e)
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [measurement, hostname, minutes])

  useEffect(() => {
    fetch()
    const interval = setInterval(fetch, 10000)
    return () => clearInterval(interval)
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}