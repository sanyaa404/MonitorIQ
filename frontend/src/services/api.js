// src/services/api.js
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

const api = axios.create({
  baseURL: `${BACKEND_URL}/api/v1`,
  timeout: 10000,
})

export const metricsApi = {
  query: (measurement, host, minutes = 30) =>
    api.get(`/metrics/query/${measurement}`, {
      params: { host, minutes }
    }).then(r => r.data),
}

export const alertsApi = {
  getRules: () => api.get('/alerts/rules').then(r => r.data),
  getEvents: () => api.get('/alerts/events').then(r => r.data),
  createRule: (rule) => api.post('/alerts/rules', rule).then(r => r.data),
  acknowledge: (id) => api.patch(`/alerts/events/${id}/acknowledge`).then(r => r.data),
}

export const authApi = {
  register: (data) => api.post('/auth/register', data).then(r => r.data),
  login: (data) => api.post('/auth/login', data).then(r => r.data),
}

export { WS_URL }
export default api