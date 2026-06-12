import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

export async function fetchLatestOEE() {
  const { data } = await api.get('/data/oee/latest')
  return data
}

export async function fetchOEEHistory(machineId: string) {
  const { data } = await api.get('/data/oee/history', { params: { machine_id: machineId } })
  return data
}

export async function fetchMachines() {
  const { data } = await api.get('/data/machines')
  return data
}

export async function fetchAlarms() {
  const { data } = await api.get('/data/alarms')
  return data
}

export async function runAnalyze(machineId: string, query: string) {
  const { data } = await api.post('/agent/analyze', { machine_id: machineId, query })
  return data
}

export async function runTroubleshoot(machineId: string, problem: string) {
  const { data } = await api.post('/agent/troubleshoot', { machine_id: machineId, problem })
  return data
}
