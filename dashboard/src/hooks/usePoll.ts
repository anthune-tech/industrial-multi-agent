import { useEffect, useState, useCallback } from 'react'

export function usePoll<T>(fetcher: () => Promise<T>, intervalMs = 30000) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      setLoading(true)
      const result = await fetcher()
      setData(result)
    } catch {
      // silently retry next poll
    } finally {
      setLoading(false)
    }
  }, [fetcher])

  useEffect(() => {
    load()
    const id = setInterval(load, intervalMs)
    return () => clearInterval(id)
  }, [load, intervalMs])

  return { data, loading, refetch: load }
}
