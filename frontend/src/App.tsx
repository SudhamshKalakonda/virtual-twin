import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Auth from './pages/Auth'
import Upload from './pages/upload'
import Chat from './pages/chat'

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [name, setName] = useState(localStorage.getItem('name') || '')
  const [partnerName, setPartnerName] = useState(localStorage.getItem('partner_name') || '')
  const [uploaded, setUploaded] = useState(localStorage.getItem('uploaded') === 'true')
  const [page, setPage] = useState(() => {
    if (!localStorage.getItem('token')) return 'auth'
    if (localStorage.getItem('uploaded') !== 'true') return 'upload'
    return 'chat'
  })

  function handleAuth(token: string, name: string, partnerName: string) {
    setToken(token)
    setName(name)
    setPartnerName(partnerName)
    setPage('upload')
  }

  function handleUpload() {
    localStorage.setItem('uploaded', 'true')
    setUploaded(true)
    setPage('chat')
  }

  if (page === 'auth') return <Auth onAuth={handleAuth} />
  if (page === 'upload') return <Upload token={token} name={name} onUpload={handleUpload} />
  return <Chat token={token} name={name} partnerName={partnerName} />
}