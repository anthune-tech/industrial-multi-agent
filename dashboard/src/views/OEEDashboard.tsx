import { usePoll } from '../hooks/usePoll'
import { fetchLatestOEE } from '../api/client'
import Gauge from '../components/Gauge'
import TrendChart from '../components/TrendChart'

export default function OEEDashboard() {
  const { data } = usePoll(fetchLatestOEE, 30000)
  const machines = Array.isArray(data) ? data : []

  return (
    <div>
      <h2>OEE Dashboard</h2>
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        {machines.map((m: any) => (
          <div key={m.machine_id} style={{
            border: '1px solid #ddd', borderRadius: 8, padding: 16, width: 260,
          }}>
            <h3 style={{ margin: '0 0 8px' }}>{m.machine_id}</h3>
            <Gauge value={m.oee ?? 0} label="OEE" />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 13 }}>
              <span>A: {(m.availability * 100).toFixed(1)}%</span>
              <span>P: {(m.performance * 100).toFixed(1)}%</span>
              <span>Q: {(m.quality * 100).toFixed(1)}%</span>
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 24 }}>
        <TrendChart />
      </div>
    </div>
  )
}
