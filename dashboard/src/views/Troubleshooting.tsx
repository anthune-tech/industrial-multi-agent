import { useState } from 'react'
import { runTroubleshoot } from '../api/client'
import ChatBubble from '../components/ChatBubble'

interface Message {
  role: 'user' | 'agent'
  text: string
}

export default function Troubleshooting() {
  const [machineId, setMachineId] = useState('LINE-03')
  const [problem, setProblem] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!problem.trim()) return
    const userMsg: Message = { role: 'user', text: problem }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)
    setProblem('')

    try {
      const res = await runTroubleshoot(machineId, problem)
      const agentMsg: Message = { role: 'agent', text: res.result }
      setMessages(prev => [...prev, agentMsg])
    } catch {
      setMessages(prev => [...prev, { role: 'agent', text: 'Error connecting to agent.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Troubleshooting Assistant</h2>
      <div style={{ marginBottom: 12 }}>
        <label>Machine: </label>
        <select value={machineId} onChange={e => setMachineId(e.target.value)}
          style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc' }}>
          {['LINE-01','LINE-02','LINE-03','LINE-04','LINE-05'].map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      <div style={{ height: 400, overflowY: 'auto', border: '1px solid #ddd', borderRadius: 8, padding: 12, marginBottom: 12, background: '#fafafa' }}>
        {messages.length === 0 && <p style={{ color: '#999' }}>Describe a problem to troubleshoot...</p>}
        {messages.map((msg, i) => (
          <ChatBubble key={i} role={msg.role} text={msg.text} />
        ))}
        {loading && <p style={{ color: '#666', fontStyle: 'italic' }}>Agent is analyzing...</p>}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={problem}
          onChange={e => setProblem(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Describe the issue..."
          style={{ flex: 1, padding: '8px 12px', borderRadius: 4, border: '1px solid #ccc' }}
        />
        <button onClick={handleSend} disabled={loading || !problem.trim()}
          style={{ padding: '8px 24px', background: '#1a73e8', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
          Send
        </button>
      </div>
    </div>
  )
}
