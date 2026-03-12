import { useState, useRef, useEffect } from 'react'

interface Message {
  id: number
  text: string
  sender: 'her' | 'me'
  time: string
}

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

async function sendMessage() {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now(),
      text: input,
      sender: 'her',
      time: getTime()
    }

    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    // Build conversation history for backend
    const history = updatedMessages.map(msg => ({
      role: msg.sender === 'her' ? 'user' : 'assistant',
      content: msg.text
    }))

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input,
          history: history.slice(0, -1)
        })
      })

      const data = await response.json()

      const botMessage: Message = {
        id: Date.now() + 1,
        text: data.reply,
        sender: 'me',
        time: getTime()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', maxWidth: '800px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ background: '#202c33', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#00a884', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>
          S
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: '15px' }}>Sudhamsh</div>
          <div style={{ fontSize: '12px', color: '#8696a0' }}>online</div>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: '4px', background: '#0b1418' }}>
        {messages.map(msg => (
          <div key={msg.id} style={{ display: 'flex', justifyContent: msg.sender === 'her' ? 'flex-start' : 'flex-end' }}>
            <div style={{
              background: msg.sender === 'her' ? '#202c33' : '#005c4b',
              padding: '8px 12px',
              borderRadius: msg.sender === 'her' ? '0px 8px 8px 8px' : '8px 0px 8px 8px',
              maxWidth: '65%',
              fontSize: '14px',
              lineHeight: '1.4'
            }}>
              {msg.text}
              <div style={{ fontSize: '11px', color: '#8696a0', textAlign: 'right', marginTop: '4px' }}>
                {msg.time}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <div style={{ background: '#005c4b', padding: '8px 16px', borderRadius: '8px 0px 8px 8px', fontSize: '20px' }}>
              ···
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ background: '#202c33', padding: '10px 16px', display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Type a message"
          rows={1}
          style={{
            flex: 1,
            background: '#2a3942',
            border: 'none',
            borderRadius: '8px',
            padding: '10px 14px',
            color: '#e9edef',
            fontSize: '15px',
            resize: 'none',
            outline: 'none',
            fontFamily: 'inherit'
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{
            background: '#00a884',
            border: 'none',
            borderRadius: '50%',
            width: '44px',
            height: '44px',
            cursor: 'pointer',
            fontSize: '18px',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          ➤
        </button>
      </div>
    </div>
  )
}