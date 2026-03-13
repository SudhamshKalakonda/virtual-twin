import { useState } from 'react'

interface Props {
  token: string
  name: string
  onUpload: () => void
}

export default function Upload({ token, name, onUpload }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState('')

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading(true)
    setError('')
    setProgress('Uploading your chats...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`http://127.0.0.1:8000/upload?token=${token}`, {
        method: 'POST',
        body: formData
      })

      const data = await res.json()

      if (!res.ok) {
        setError(data.detail || 'Upload failed')
        return
      }

      setProgress(`✅ ${data.total_messages} messages processed!`)
      setTimeout(() => onUpload(), 1500)

    } catch (e) {
      setError('Cannot connect to server')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#111b21'
    }}>
      <div style={{
        background: '#202c33',
        padding: '40px',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '400px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        textAlign: 'center'
      }}>
        <div>
          <div style={{ fontSize: '48px' }}>💬</div>
          <h2 style={{ color: '#e9edef', fontSize: '20px', marginTop: '8px' }}>
            Hey {name}! Upload your chats
          </h2>
          <p style={{ color: '#8696a0', fontSize: '13px', marginTop: '8px', lineHeight: 1.6 }}>
            Export your WhatsApp chat as a .txt file and upload it here.
            Your data stays private and is never shared.
          </p>
        </div>

        <label style={{
          background: '#2a3942',
          border: '2px dashed #3d5a6a',
          borderRadius: '12px',
          padding: '32px',
          cursor: 'pointer',
          display: 'block',
          transition: 'all 0.2s'
        }}>
          <div style={{ fontSize: '32px' }}>📁</div>
          <p style={{ color: '#00a884', fontWeight: 600, marginTop: '8px' }}>
            {loading ? progress : 'Click to upload .txt file'}
          </p>
          <input
            type="file"
            accept=".txt"
            onChange={handleFile}
            style={{ display: 'none' }}
            disabled={loading}
          />
        </label>

        {error && (
          <p style={{ color: '#f15c6d', fontSize: '13px' }}>{error}</p>
        )}

        <p style={{ color: '#8696a0', fontSize: '12px' }}>
          🔒 End-to-end private. We never read your messages.
        </p>
      </div>
    </div>
  )
}