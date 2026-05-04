import { useState } from 'react'
import Chat from './components/Chat'
import ArchitectReview from './components/ArchitectReview'
import ApiContractReview from './components/ApiContractReview'

function App() {
  const [phase, setPhase] = useState('planner')
  const [brief, setBrief] = useState('')
  const [architecture, setArchitecture] = useState(null)
  const [contract, setContract] = useState(null)

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {phase === 'planner' && (
        <Chat onBriefConfirmed={(b) => { setBrief(b); setPhase('architect') }} />
      )}
      {phase === 'architect' && (
        <ArchitectReview brief={brief} onApprove={(a) => { setArchitecture(a); setPhase('api-contract') }} />
      )}
      {phase === 'api-contract' && (
        <ApiContractReview architecture={architecture} onApprove={(c) => { setContract(c); setPhase('done') }} />
      )}
      {phase === 'done' && (
        <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px' }}>
          <h2>✅ API Contract Approved!</h2>
          <p style={{ color: '#888' }}>Frontend Coder Agent coming next...</p>
          <pre style={{ background: '#1e1e1e', color: '#d4d4d4', padding: '16px', borderRadius: '8px', fontSize: '13px' }}>
            {JSON.stringify(contract, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default App