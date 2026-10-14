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
    <div>
      {error && <p>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          Start:
          <input type="text" list="digimon-names" value={start} disabled={loading} onChange={(e) => setStart(e.target.value)} />
        </label>
        <label>
          Target:
          <input type="text" list="digimon-names" value={target} disabled={loading} onChange={(e) => setTarget(e.target.value)} />
        </label>
        <button type="submit" disabled={loading}>Go</button>
      </form>
      <datalist id="digimon-names">
        {digimon.map((d) => (
          <option key={d.name} value={d.name}>{d.stage}</option>
        ))}
      </datalist>

      {formErrors.map((message) => <p key={message}>{message}</p>)}
      {pathError && <p>{pathError}</p>}
      {loading && <p>Searching...</p>}

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
