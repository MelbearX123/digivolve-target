import { useEffect, useState } from 'react'
import type { SubmitEvent } from 'react'

import './App.css'
import Combobox from './Combobox'
import Footer from './Footer'
import { ABORT_ERROR, ApiRoute } from './api'
import { Kind } from './types'
import type { Digimon, PathResponse, Requirements } from './types'

const KIND_LABELS: Record<Kind, string> = {
  [Kind.Evolve]: 'Evolve to',
  [Kind.Devolve]: 'De-evolve to',
  [Kind.Swap]: 'Swap to',
}

function formatRequirements(requirements: Requirements) {
  return Object.entries(requirements)
    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(' + ') : value}`)
    .join(', ')
}

function App() {
  const [digimon, setDigimon] = useState<Digimon[]>([])
  const [error, setError] = useState('')
  const [start, setStart] = useState('')
  const [target, setTarget] = useState('')
  const [formErrors, setFormErrors] = useState<string[]>([])
  const [path, setPath] = useState<PathResponse | null>(null)
  const [pathError, setPathError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    fetch(ApiRoute.Digimon, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`GET ${ApiRoute.Digimon} failed: ${res.status}`)
        return res.json() as Promise<Digimon[]>
      })
      .then(setDigimon)
      .catch((err: Error) => {
        if (err.name !== ABORT_ERROR) setError(err.message)
      })
    return () => controller.abort()
  }, [])

  async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault()
    const startName = start.trim()
    const targetName = target.trim()

    const errors = []
    if (!startName) errors.push('Start is required.')
    if (!targetName) errors.push('Target is required.')
    setFormErrors(errors)
    setPath(null)
    setPathError('')
    if (errors.length > 0) return

    setLoading(true)
    try {
      const params = new URLSearchParams({ start: startName, target: targetName })
      const res = await fetch(`${ApiRoute.Path}?${params}`)
      const body = await res.json()
      if (!res.ok) {
        setPathError(typeof body.detail === 'string' ? body.detail : `GET ${ApiRoute.Path} failed: ${res.status}`)
        return
      }
      setPath(body as PathResponse)
    } catch {
      setPathError('Could not reach the server.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="app">
        <header className="header">
          <h1 className="title">Digi-Target</h1>
          <p className="subtitle">
            Find the fastest way to get from one Digimon to another in Digimon Story: Time Stranger
          </p>
        </header>
        {error && <p className="error messages">{error}</p>}
        <form className="search-form" onSubmit={handleSubmit}>
          <div className="fields">
            <Combobox label="Start:" value={start} options={digimon} disabled={loading} onChange={setStart} />
            <Combobox label="Target:" value={target} options={digimon} disabled={loading} onChange={setTarget} />
          </div>
          <button className="go-button" type="submit" disabled={loading}>Go</button>
        </form>

        <div className="messages">
          {formErrors.map((message) => <p key={message} className="error">{message}</p>)}
          {pathError && <p className="error">{pathError}</p>}
          {loading && <p className="status">Searching...</p>}
        </div>

        {path && (
          path.steps.length === 0 ? (
            <p>{path.start} is already {path.target}.</p>
          ) : (
            <ol>
              <li>{path.start}</li>
              {path.steps.map((step, i) => (
                <li key={i}>
                  {KIND_LABELS[step.kind]} {step.to}
                  {Object.keys(step.requirements).length > 0 && ` (${formatRequirements(step.requirements)})`}
                </li>
              ))}
            </ol>
          )
        )}
      </div>
      <Footer />
    </>
  )
}

export default App
