import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

export default function Chat({ onBriefConfirmed }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your project planning assistant. What would you like to build?" }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [confirmed, setConfirmed] = useState(false)
  const [brief, setBrief] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const history = newMessages.slice(0, -1)
      const res = await axios.post(`${API_URL}/planner/chat`, {
        message: input,
        history: history
      })

      const assistantMessage = { role: 'assistant', content: res.data.reply }
      setMessages([...newMessages, assistantMessage])

      if (res.data.confirmed) {
        setConfirmed(true)
        setBrief(res.data.brief)
      }
    } catch (err) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: 'Something went wrong. Please try again.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', maxWidth: '800px', margin: '0 auto', padding: '20px' }}>

      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ margin: 0 }}>🧠 Project Planner</h2>
        <p style={{ margin: '4px 0 0', color: '#888', fontSize: '14px' }}>Describe your project idea and I'll help you finalize it</p>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '75%',
            padding: '10px 14px',
            borderRadius: '12px',
            background: msg.role === 'user' ? '#0070f3' : '#f0f0f0',
            color: msg.role === 'user' ? 'white' : 'black',
            whiteSpace: 'pre-wrap',
            fontSize: '14px',
            lineHeight: '1.5'
          }}>
            {msg.content}
          </div>
        ))}

        {loading && (
          <div style={{ alignSelf: 'flex-start', padding: '10px 14px', borderRadius: '12px', background: '#f0f0f0', color: '#888', fontSize: '14px' }}>
            Thinking...
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Confirmed Brief */}
      {confirmed && (
        <div style={{ marginBottom: '16px', padding: '16px', background: '#f0fff4', border: '1px solid #68d391', borderRadius: '8px' }}>
          <p style={{ margin: '0 0 12px', fontWeight: 'bold', color: '#276749' }}>✅ Project Brief Confirmed!</p>
          <pre style={{ margin: '0 0 12px', fontSize: '13px', whiteSpace: 'pre-wrap', color: '#2d3748' }}>{brief}</pre>
          <button
            onClick={() => onBriefConfirmed(brief)}
            style={{ padding: '8px 16px', background: '#38a169', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            Continue to Architecture →
          </button>
        </div>
      )}

      {/* Input */}
      {!confirmed && (
        <div style={{ display: 'flex', gap: '8px' }}>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Enter to send)"
            rows={2}
            style={{ flex: 1, padding: '10px', borderRadius: '8px', border: '1px solid #ddd', resize: 'none', fontSize: '14px', fontFamily: 'inherit' }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{ padding: '10px 20px', background: '#0070f3', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', opacity: loading || !input.trim() ? 0.5 : 1 }}
          >
            Send
          </button>
        </div>
      )}
    </div>
  )
}