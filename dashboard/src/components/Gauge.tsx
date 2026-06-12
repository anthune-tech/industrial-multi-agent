interface GaugeProps {
  value: number
  label: string
}

export default function Gauge({ value, label }: GaugeProps) {
  const pct = Math.min(value * 100, 100)
  const color = pct >= 85 ? '#34a853' : pct >= 60 ? '#fbbc04' : '#ea4335'

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: 80, height: 80, borderRadius: '50%',
        border: `6px solid ${color}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto', fontSize: 20, fontWeight: 700,
      }}>
        {pct.toFixed(0)}%
      </div>
      <div style={{ marginTop: 4, fontSize: 13, color: '#666' }}>{label}</div>
    </div>
  )
}
