import { useState } from 'react'
import { usePoll } from '../hooks/usePoll'
import { fetchLatestOEE, OeeSnapshot } from '../api/client'
import Gauge from '../components/Gauge'
import TrendChart from '../components/TrendChart'

export default function OEEDashboard() {
  const { data } = usePoll<OeeSnapshot[]>(fetchLatestOEE, 30000)
  const [selectedMachine, setSelectedMachine] = useState('LINE-01')
  const machines = Array.isArray(data) ? data : []

  return (
    <div>
      <h2>OEE Dashboard</h2>
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        {machines.map((m) => (
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
        <div style={{ marginBottom: 12 }}>
          <label>Machine: </label>
          <select value={selectedMachine} onChange={e => setSelectedMachine(e.target.value)}
            style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc' }}>
            {['LINE-01','LINE-02','LINE-03','LINE-04','LINE-05'].map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
        <TrendChart machineId={selectedMachine} />
      </div>
    </div>
  )
}