import { useEffect, useState } from 'react'
import type { SubmitEvent } from 'react'

import './App.css'

type Digimon = {
  name: string
  stage: string
}

const Kind = {
  Evolve: 'evolve',
  Devolve: 'devolve',
  Swap: 'swap',
} as const

type Kind = (typeof Kind)[keyof typeof Kind]

const KIND_LABELS: Record<Kind, string> = {
  [Kind.Evolve]: 'Evolve to',
  [Kind.Devolve]: 'De-evolve to',
  [Kind.Swap]: 'Swap to',
}

type Requirements = Record<string, number | string | string[]>

type Step = {
  to: string
  kind: Kind
  requirements: Requirements
}

type PathResponse = {
  start: string
  target: string
  steps: Step[]
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
    fetch('/api/digimon', { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`GET /digimon failed: ${res.status}`)
        return res.json() as Promise<Digimon[]>
      })
      .then(setDigimon)
      .catch((err: Error) => {
        if (err.name !== 'AbortError') setError(err.message)
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
      const res = await fetch(`/api/path?${params}`)
      const body = await res.json()
      if (!res.ok) {
        setPathError(typeof body.detail === 'string' ? body.detail : `GET /path failed: ${res.status}`)
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
          <label className="field">
            Start:
            <input type="text" list="digimon-names" value={start} disabled={loading} onChange={(e) => setStart(e.target.value)} />
          </label>
          <label className="field">
            Target:
            <input type="text" list="digimon-names" value={target} disabled={loading} onChange={(e) => setTarget(e.target.value)} />
          </label>
        </div>
        <button className="go-button" type="submit" disabled={loading}>Go</button>
      </form>
      <datalist id="digimon-names">
        {digimon.map((d) => (
          <option key={d.name} value={d.name}>{d.stage}</option>
        ))}
      </datalist>

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
  )
}

export default App
