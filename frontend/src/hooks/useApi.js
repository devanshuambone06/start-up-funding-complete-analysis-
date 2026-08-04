/**
 * useApi.js - Generic data-fetching hook with loading/error states
 */
import { useState, useEffect, useCallback, useRef } from 'react'

export function useApi(apiFn, deps = [], immediate = true) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)
  const apiFnRef = useRef(apiFn)
  apiFnRef.current = apiFn

  const execute = useCallback(async (...args) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiFnRef.current(...args)
      setData(result)
      return result
    } catch (err) {
      setError(err?.message || 'Request failed')
      return null
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    if (immediate) execute()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [execute])

  return { data, loading, error, refetch: execute }
}

export function LoadingSpinner({ size = 'md', className = '' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }
  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div className={`${sizes[size]} border-2 border-violet-500 border-t-transparent rounded-full animate-spin`} />
    </div>
  )
}

export function ApiError({ error, fallback = null }) {
  if (!error) return fallback
  return (
    <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
      ⚠️ {error} — showing cached data
    </div>
  )
}
