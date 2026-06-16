import { useEffect, useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { fetchOEEHistory, OeeSnapshot } from '../api/client'

interface TrendChartProps {
  machineId?: string
}

export default function TrendChart({ machineId = 'LINE-01' }: TrendChartProps) {
  const [data, setData] = useState<OeeSnapshot[]>([])

  useEffect(() => {
    fetchOEEHistory(machineId).then(setData).catch(() => {})
  }, [machineId])

  const chartData = data.map(d => ({
    time: new Date(d.timestamp).toLocaleString('en-US', { hour: '2-digit', minute: '2-digit' }),
    OEE: +(d.oee * 100).toFixed(1),
    Availability: +(d.availability * 100).toFixed(1),
    Performance: +(d.performance * 100).toFixed(1),
    Quality: +(d.quality * 100).toFixed(1),
  })).reverse()

  if (chartData.length === 0) {
    return (
      <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8, background: '#fff' }}>
        <h4 style={{ margin: '0 0 12px' }}>OEE Trend (24h) — {machineId}</h4>
        <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
          No data available
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8, background: '#fff' }}>
      <h4 style={{ margin: '0 0 12px' }}>OEE Trend (24h) — {machineId}</h4>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" fontSize={11} />
          <YAxis domain={[0, 100]} unit="%" fontSize={11} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="OEE" stroke="#1a73e8" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="Availability" stroke="#34a853" strokeWidth={1} dot={false} />
          <Line type="monotone" dataKey="Performance" stroke="#fbbc04" strokeWidth={1} dot={false} />
          <Line type="monotone" dataKey="Quality" stroke="#ea4335" strokeWidth={1} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}