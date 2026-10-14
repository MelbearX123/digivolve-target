import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Mock } from 'vitest'

import App from './App'
import { ApiRoute } from './api'
import { Kind } from './types'
import type { Digimon, PathResponse } from './types'

const DIGIMON: Digimon[] = [
  { name: 'Agumon', stage: 'Rookie' },
  { name: 'BlitzGreymon', stage: 'Mega' },
  { name: 'Gabumon', stage: 'Rookie' },
  { name: 'Greymon', stage: 'Champion' },
]

const PATH: PathResponse = {
  start: 'Agumon',
  target: 'Greymon',
  steps: [{ to: 'Greymon', kind: Kind.Evolve, requirements: { 'Agent Rank': 3 } }],
}

let fetchMock: Mock<typeof fetch>

function jsonResponse(body: unknown) {
  return Promise.resolve(new Response(JSON.stringify(body), { status: 200 }))
}

function callsTo(route: string) {
  return fetchMock.mock.calls.filter(([url]) => String(url).startsWith(route))
}

async function renderLoaded() {
  render(<App />)
  await waitFor(() => expect(callsTo(ApiRoute.Digimon)).toHaveLength(1))
}

function optionNames() {
  return screen.getAllByRole('option').map((option) => option.firstChild?.textContent)
}

beforeEach(() => {
  fetchMock = vi.fn<typeof fetch>((input) => {
    const url = String(input)
    if (url.startsWith(ApiRoute.Digimon)) return jsonResponse(DIGIMON)
    if (url.startsWith(ApiRoute.Path)) return jsonResponse(PATH)
    return Promise.reject(new Error(`Unexpected fetch: ${url}`))
  })
  vi.stubGlobal('fetch', fetchMock)
})

describe('App', () => {
  it('calls the digimon API once on load', async () => {
    await renderLoaded()

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(callsTo(ApiRoute.Path)).toHaveLength(0)
  })

  it('filters the dropdown when typing in Start', async () => {
    const user = userEvent.setup()
    await renderLoaded()

    await user.type(screen.getByRole('combobox', { name: 'Start:' }), 'grey')

    expect(optionNames()).toEqual(['Greymon', 'BlitzGreymon'])
  })

  it('filters the dropdown when typing in Target', async () => {
    const user = userEvent.setup()
    await renderLoaded()

    await user.type(screen.getByRole('combobox', { name: 'Target:' }), 'gabu')

    expect(optionNames()).toEqual(['Gabumon'])
  })

  it('calls the path API once when pressing Go', async () => {
    const user = userEvent.setup()
    await renderLoaded()

    await user.type(screen.getByRole('combobox', { name: 'Start:' }), 'Agumon')
    await user.type(screen.getByRole('combobox', { name: 'Target:' }), 'Greymon')
    await user.click(screen.getByRole('button', { name: 'Go' }))

    await screen.findByText(/Evolve to Greymon/)
    const pathCalls = callsTo(ApiRoute.Path)
    expect(pathCalls).toHaveLength(1)
    expect(pathCalls[0][0]).toBe(`${ApiRoute.Path}?start=Agumon&target=Greymon`)
  })
})
