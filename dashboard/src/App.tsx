import { useState } from 'react'
import OEEDashboard from './views/OEEDashboard'
import MachineOverview from './views/MachineOverview'
import DataAnalytics from './views/DataAnalytics'
import Troubleshooting from './views/Troubleshooting'

const TABS = [
  { key: 'oee', label: 'OEE Dashboard' },
  { key: 'machines', label: 'Machine Overview' },
  { key: 'analytics', label: 'Data Analytics' },
  { key: 'troubleshoot', label: 'Troubleshooting' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('oee')

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: 24 }}>
      <h1 style={{ margin: 0, marginBottom: 24 }}>Plant Management Dashboard</h1>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            style={{
              padding: '8px 20px',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer',
              fontWeight: activeTab === t.key ? 700 : 400,
              background: activeTab === t.key ? '#1a73e8' : '#e8eaed',
              color: activeTab === t.key ? '#fff' : '#333',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>
      {activeTab === 'oee' && <OEEDashboard />}
      {activeTab === 'machines' && <MachineOverview />}
      {activeTab === 'analytics' && <DataAnalytics />}
      {activeTab === 'troubleshoot' && <Troubleshooting />}
    </div>
  )
}
