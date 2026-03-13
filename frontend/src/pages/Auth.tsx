import { useState } from 'react'

interface Props {
  onAuth: (token: string, name: string, partnerName: string) => void
}

export default function Auth({ onAuth }: Props) {
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '',
    whatsapp_name: '',
    partner_name: '',
    email: '',
    password: ''
  })

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleSubmit() {
    setLoading(true)
    setError('')

    const url = isLogin
      ? 'http://127.0.0.1:8000/login'
      : 'http://127.0.0.1:8000/signup'

    const body = isLogin
      ? { email: form.email, password: form.password }
      : form

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      const data = await res.json()

      if (!res.ok) {
        setError(data.detail || 'Something went wrong')
        return
      }

      localStorage.setItem('token', data.token)
      localStorage.setItem('name', data.name)
      localStorage.setItem('partner_name', data.partner_name)
      onAuth(data.token, data.name, data.partner_name)

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
        gap: '16px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '8px' }}>
          <div style={{ fontSize: '32px' }}>🤖</div>
          <h1 style={{ fontSize: '22px', fontWeight: 700, color: '#e9edef' }}>Virtual Twin</h1>
          <p style={{ fontSize: '13px', color: '#8696a0', marginTop: '4px' }}>
            Your chats are private and never shared
          </p>
        </div>

        {/* Toggle */}
        <div style={{ display: 'flex', background: '#2a3942', borderRadius: '8px', padding: '4px' }}>
          {['Login', 'Sign Up'].map((label, i) => (
            <button key={label} onClick={() => setIsLogin(i === 0)} style={{
              flex: 1,
              padding: '8px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 600,
              background: isLogin === (i === 0) ? '#00a884' : 'transparent',
              color: isLogin === (i === 0) ? 'white' : '#8696a0',
              transition: 'all 0.2s'
            }}>{label}</button>
          ))}
        </div>

        {!isLogin && (
  <>
    <input name="name" placeholder="Your display name (e.g. Sudhamsh)" value={form.name}
      onChange={handleChange} style={inputStyle} />
    <input name="whatsapp_name" placeholder="Your name in WhatsApp export (e.g. Sudhamsh K)" value={form.whatsapp_name}
      onChange={handleChange} style={inputStyle} />
    <input name="partner_name" placeholder="Your partner's name" value={form.partner_name}
      onChange={handleChange} style={inputStyle} />
  </>
)}

        <input name="email" placeholder="Email" value={form.email} type="email"
          onChange={handleChange} style={inputStyle} />
        <input name="password" placeholder="Password" value={form.password} type="password"
          onChange={handleChange} style={inputStyle} />

        {error && <p style={{ color: '#f15c6d', fontSize: '13px', textAlign: 'center' }}>{error}</p>}

        <button onClick={handleSubmit} disabled={loading} style={{
          background: '#00a884',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          padding: '14px',
          fontSize: '15px',
          fontWeight: 700,
          cursor: 'pointer',
          opacity: loading ? 0.7 : 1
        }}>
          {loading ? 'Please wait...' : isLogin ? 'Login' : 'Create Account'}
        </button>
      </div>
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  background: '#2a3942',
  border: 'none',
  borderRadius: '8px',
  padding: '12px 16px',
  color: '#e9edef',
  fontSize: '14px',
  outline: 'none',
  width: '100%'
}