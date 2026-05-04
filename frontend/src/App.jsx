import { useState } from 'react'
import Chat from './components/Chat'
import ArchitectReview from './components/ArchitectReview'

function App() {
  const [phase, setPhase] = useState('planner')
  const [brief, setBrief] = useState('')
  const [architecture, setArchitecture] = useState(null)

  const handleBriefConfirmed = (confirmedBrief) => {
    setBrief(confirmedBrief)
    setPhase('architect')
  }

  const handleArchitectureApproved = (approvedArchitecture) => {
    setArchitecture(approvedArchitecture)
    setPhase('done') // sonraki phase gelince güncellenecek
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {phase === 'planner' && (
        <Chat onBriefConfirmed={handleBriefConfirmed} />
      )}
      {phase === 'architect' && (
        <ArchitectReview brief={brief} onApprove={handleArchitectureApproved} />
      )}
      {phase === 'done' && (
        <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px' }}>
          <h2>✅ Architecture Approved!</h2>
          <p style={{ color: '#888' }}>API Contract Agent coming next...</p>
          <pre style={{ background: '#1e1e1e', color: '#d4d4d4', padding: '16px', borderRadius: '8px', fontSize: '13px' }}>
            {JSON.stringify(architecture, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default App