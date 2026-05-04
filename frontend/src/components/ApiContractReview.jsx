import { useState } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

export default function ApiContractReview({ architecture, onApprove }) {
  const [contract, setContract] = useState(null)
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [editMode, setEditMode] = useState(false)
  const [editedJson, setEditedJson] = useState('')
  const [error, setError] = useState('')

  const generate = async (feedbackText = '') => {
    setLoading(true)
    setError('')
    try {
      const archToSend = feedbackText
        ? { ...architecture, user_feedback: feedbackText }
        : architecture
      const res = await axios.post(`${API_URL}/api-contract/generate`, { architecture: archToSend })
      setContract(res.data.contract)
      setEditedJson(JSON.stringify(res.data.contract, null, 2))
      setFeedback('')
      setEditMode(false)
    } catch (err) {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = () => {
    if (editMode) {
      try {
        const parsed = JSON.parse(editedJson)
        onApprove(parsed)
      } catch {
        setError('Invalid JSON. Please fix before approving.')
      }
    } else {
      onApprove(contract)
    }
  }

  const handleRetry = () => {
    if (!feedback.trim()) return
    generate(feedback)
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h2 style={{ marginBottom: '4px' }}>📋 API Contract Review</h2>
      <p style={{ color: '#888', fontSize: '14px', marginBottom: '20px' }}>
        Review the OpenAPI spec — this is the contract between frontend and backend
      </p>

      {!contract && !loading && (
        <button
          onClick={() => generate()}
          style={{ padding: '10px 20px', background: '#0070f3', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          Generate API Contract
        </button>
      )}

      {loading && (
        <div style={{ padding: '20px', background: '#f0f0f0', borderRadius: '8px', color: '#888' }}>
          ⏳ Generating API contract...
        </div>
      )}

      {error && (
        <div style={{ padding: '12px', background: '#fff5f5', border: '1px solid #fc8181', borderRadius: '8px', color: '#c53030', marginBottom: '16px' }}>
          {error}
        </div>
      )}

      {contract && !loading && (
        <>
          <div style={{ marginBottom: '16px' }}>
            {editMode ? (
              <textarea
                value={editedJson}
                onChange={e => setEditedJson(e.target.value)}
                style={{ width: '100%', height: '400px', fontFamily: 'monospace', fontSize: '13px', padding: '12px', borderRadius: '8px', border: '1px solid #ddd', boxSizing: 'border-box' }}
              />
            ) : (
              <pre style={{ background: '#1e1e1e', color: '#d4d4d4', padding: '16px', borderRadius: '8px', overflow: 'auto', fontSize: '13px', maxHeight: '400px' }}>
                {JSON.stringify(contract, null, 2)}
              </pre>
            )}
          </div>

          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
            <button
              onClick={handleApprove}
              style={{ padding: '10px 20px', background: '#38a169', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              ✅ Approve
            </button>
            <button
              onClick={() => setEditMode(!editMode)}
              style={{ padding: '10px 20px', background: '#718096', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              {editMode ? '👁️ Preview' : '✏️ Edit'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleRetry()}
              placeholder="Give feedback to regenerate (e.g. add pagination to list endpoints)"
              style={{ flex: 1, padding: '10px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '14px' }}
            />
            <button
              onClick={handleRetry}
              disabled={!feedback.trim()}
              style={{ padding: '10px 20px', background: '#ed8936', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', opacity: !feedback.trim() ? 0.5 : 1 }}
            >
              🔄 Retry
            </button>
          </div>
        </>
      )}
    </div>
  )
}