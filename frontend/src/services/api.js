/**
 * api.js - Centralized Axios API service
 * All backend communication goes through this file.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach user email header for logging purposes
api.interceptors.request.use((config) => {
  try {
    const user = localStorage.getItem('sfa_user') || sessionStorage.getItem('sfa_user')
    if (user) {
      const parsed = JSON.parse(user)
      if (parsed?.email) config.headers['X-User'] = parsed.email
    }
  } catch (_) { /* ignore parse errors */ }
  return config
})

// Unwrap data, handle fallback gracefully if server is spinning up
api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const url = err.config?.url || ''
    const msg = err.response?.data?.detail || err.message || 'Unknown error'
    console.warn(`[API Notice] ${url} — ${msg}. Server spinning up...`)
    return Promise.reject(err)
  }
)

// ── Endpoint helpers ──────────────────────────────────────────────────────────
export const healthCheck       = ()         => api.get('/api/health')
export const fetchOverview     = ()         => api.get('/api/overview')
export const fetchFundingTrends = ()        => api.get('/api/funding/trends')
export const fetchSectors      = ()         => api.get('/api/sectors')
export const fetchStartups     = (params={})=> api.get('/api/startups', { params })
export const fetchInvestors    = ()         => api.get('/api/investors')
export const fetchInvestorList = ()         => api.get('/api/investors/list')
export const fetchGeographic   = ()         => api.get('/api/geographic')
export const fetchOpportunity  = ()         => api.get('/api/opportunity')
export const fetchReports      = ()         => api.get('/api/reports')
export const runPrediction     = (payload)  => api.post('/api/predict', payload)
export const fetchOptions      = ()         => api.get('/api/options')
export const addStartup        = (payload)  => api.post('/api/startups/add', payload)

export const getExportUrl = (params = {}) => {
  const qs = new URLSearchParams(params).toString()
  return `${BASE_URL}/api/export/csv${qs ? '?' + qs : ''}`
}

export default api
