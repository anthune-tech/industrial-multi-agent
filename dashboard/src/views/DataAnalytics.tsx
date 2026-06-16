import { useState } from 'react'
import { runAnalyze } from '../api/client'

const MACHINES = ['LINE-01','LINE-02','LINE-03','LINE-04','LINE-05']

export default function DataAnalytics() {
  const [machineId, setMachineId] = useState('LINE-01')
  const [query, setQuery] = useState('Show me the OEE trend for last 7 days')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    try {
      const res = await runAnalyze(machineId, query)
      setResult(res.result)
    } catch {
      setResult('Error running analysis')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Data Analytics</h2>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center' }}>
        <label>Machine:</label>
        <select value={machineId} onChange={e => setMachineId(e.target.value)}
          style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc' }}>
          {MACHINES.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: 12 }}>
        <textarea
          value={query}
          onChange={e => setQuery(e.target.value)}
          rows={3}
          style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
        />
      </div>
      <button onClick={handleRun} disabled={loading}
        style={{ padding: '8px 24px', background: '#1a73e8', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
        {loading ? 'Running...' : 'Run Analysis'}
      </button>
      {result && (
        <pre style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 6, whiteSpace: 'pre-wrap' }}>
          {result}
        </pre>
      )}
    </div>
  )
}