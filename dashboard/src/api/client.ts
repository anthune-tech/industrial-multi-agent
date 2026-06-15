import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

export interface OeeSnapshot {
  id: number
  machine_id: string
  timestamp: string
  shift: string
  availability: number
  performance: number
  quality: number
  oee: number
  run_minutes: number
  downtime_minutes: number
}

export interface MachineStatus {
  machine_id: string
  status: 'running' | 'idle' | 'down' | 'maintenance'
  last_seen: string
  error_code: string | null
  oee_current: number
  updated_at: string
}

export interface Alarm {
  id: number
  machine_id: string
  severity: 'info' | 'warning' | 'critical'
  message: string
  details: Record<string, unknown>
  triggered_at: string
  acknowledged: boolean
}

export interface AnalyticsResult {
  id: number
  query_type: string
  machine_id: string
  parameters: Record<string, unknown>
  result: Record<string, unknown>
  created_at: string
}

export async function fetchLatestOEE(): Promise<OeeSnapshot[]> {
  const { data } = await api.get('/data/oee/latest')
  return data
}

export async function fetchOEEHistory(machineId: string): Promise<OeeSnapshot[]> {
  const { data } = await api.get('/data/oee/history', { params: { machine_id: machineId } })
  return data
}

export async function fetchMachines(): Promise<MachineStatus[]> {
  const { data } = await api.get('/data/machines')
  return data
}

export async function fetchAlarms(): Promise<Alarm[]> {
  const { data } = await api.get('/data/alarms')
  return data
}

export async function runAnalyze(machineId: string, query: string): Promise<{ result: string }> {
  const { data } = await api.post('/agent/analyze', { machine_id: machineId, query })
  return data
}

export async function runTroubleshoot(machineId: string, problem: string): Promise<{ result: string }> {
  const { data } = await api.post('/agent/troubleshoot', { machine_id: machineId, problem })
  return data
}