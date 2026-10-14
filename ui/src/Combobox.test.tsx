import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it } from 'vitest'

import Combobox from './Combobox'
import type { Digimon } from './types'

const DIGIMON: Digimon[] = [
  { name: 'Agumon', stage: 'Rookie' },
  { name: 'BlitzGreymon', stage: 'Mega' },
  { name: 'Greymon', stage: 'Champion' },
]

function Form() {
  const [start, setStart] = useState('')
  const [target, setTarget] = useState('')
  return (
    <>
      <Combobox label="Start:" value={start} options={DIGIMON} onChange={setStart} />
      <Combobox label="Target:" value={target} options={DIGIMON} onChange={setTarget} />
    </>
  )
}

function activeOption() {
  return screen.getAllByRole('option').find((option) => option.getAttribute('aria-selected') === 'true')
}

describe('Combobox', () => {
  it('Tab moves through the list after typing and Enter selects', async () => {
    const user = userEvent.setup()
    render(<Form />)
    const start = screen.getByRole('combobox', { name: 'Start:' })

    await user.type(start, 'grey')
    await user.tab()
    expect(activeOption()).toHaveTextContent('Greymon')
    await user.tab()
    expect(activeOption()).toHaveTextContent('BlitzGreymon')
    await user.tab({ shift: true })
    expect(activeOption()).toHaveTextContent('Greymon')
    expect(start).toHaveFocus()

    await user.keyboard('{Enter}')
    expect(start).toHaveValue('Greymon')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('Tab moves to the next field when nothing was typed', async () => {
    const user = userEvent.setup()
    render(<Form />)

    await user.click(screen.getByRole('combobox', { name: 'Start:' }))
    await user.tab()
    expect(screen.getByRole('combobox', { name: 'Target:' })).toHaveFocus()
  })

  it('Tab moves to the next field after selecting', async () => {
    const user = userEvent.setup()
    render(<Form />)

    await user.type(screen.getByRole('combobox', { name: 'Start:' }), 'agu')
    await user.tab()
    await user.keyboard('{Enter}')
    await user.tab()
    expect(screen.getByRole('combobox', { name: 'Target:' })).toHaveFocus()
  })
})
