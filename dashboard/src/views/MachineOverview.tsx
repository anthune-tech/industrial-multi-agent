import { usePoll } from '../hooks/usePoll'
import { fetchMachines } from '../api/client'
import StatusCard from '../components/StatusCard'

export default function MachineOverview() {
  const { data } = usePoll(fetchMachines, 30000)
  const machines = Array.isArray(data) ? data : []

  return (
    <div>
      <h2>Machine Overview</h2>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {machines.map((m: any) => (
          <StatusCard key={m.machine_id} machine={m} />
        ))}
      </div>
    </div>
  )
}
