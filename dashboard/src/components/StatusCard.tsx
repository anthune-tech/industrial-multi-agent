interface Machine {
  machine_id: string
  status: string
  last_seen: string
  error_code: string | null
  oee_current: number
}

const STATUS_COLORS: Record<string, string> = {
  running: '#34a853',
  idle: '#fbbc04',
  down: '#ea4335',
  maintenance: '#9334e6',
}

export default function StatusCard({ machine }: { machine: Machine }) {
  const color = STATUS_COLORS[machine.status] || '#999'
  const oeePct = (machine.oee_current ?? 0) * 100

  return (
    <div style={{
      border: `1px solid ${color}`,
      borderLeft: `6px solid ${color}`,
      borderRadius: 8, padding: 16, width: 220,
      background: '#fff',
    }}>
      <h3 style={{ margin: '0 0 8px' }}>{machine.machine_id}</h3>
      <div style={{ fontSize: 13, lineHeight: 1.8 }}>
        <div>Status: <strong style={{ color }}>{machine.status}</strong></div>
        <div>OEE: {oeePct.toFixed(1)}%</div>
        <div>Last: {new Date(machine.last_seen).toLocaleString()}</div>
        {machine.error_code && <div>Error: {machine.error_code}</div>}
      </div>
    </div>
  )
}
