import { usePoll } from '../hooks/usePoll'
import { fetchMachines, MachineStatus } from '../api/client'
import StatusCard from '../components/StatusCard'

export default function MachineOverview() {
  const { data } = usePoll<MachineStatus[]>(fetchMachines, 30000)
  const machines = Array.isArray(data) ? data : []

  return (
    <div>
      <h2>Machine Overview</h2>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {machines.map((m) => (
          <StatusCard key={m.machine_id} machine={m} />
        ))}
      </div>
    </div>
  )
}