import { useEffect, useId, useMemo, useState } from 'react'
import type { KeyboardEvent } from 'react'

import type { Digimon } from './types'

const Key = {
  ArrowDown: 'ArrowDown',
  ArrowUp: 'ArrowUp',
  Enter: 'Enter',
  Escape: 'Escape',
} as const

function optionId(comboboxId: string, index: number) {
  return `${comboboxId}-option-${index}`
}

type ComboboxProps = {
  label: string
  value: string
  options: Digimon[]
  disabled?: boolean
  onChange: (value: string) => void
}

function filterOptions(options: Digimon[], query: string) {
  const q = query.trim().toLowerCase()
  if (!q) return options
  const startsWith: Digimon[] = []
  const contains: Digimon[] = []
  for (const option of options) {
    const name = option.name.toLowerCase()
    if (name.startsWith(q)) startsWith.push(option)
    else if (name.includes(q)) contains.push(option)
  }
  return [...startsWith, ...contains]
}

function Combobox({ label, value, options, disabled = false, onChange }: ComboboxProps) {
  const id = useId()
  const inputId = `${id}-input`
  const listboxId = `${id}-listbox`

  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)

  const filtered = useMemo(() => filterOptions(options, value), [options, value])
  const showList = open && !disabled && filtered.length > 0

  useEffect(() => {
    if (activeIndex < 0) return
    document.getElementById(optionId(id, activeIndex))?.scrollIntoView({ block: 'nearest' })
  }, [id, activeIndex])

  function select(option: Digimon) {
    onChange(option.name)
    setOpen(false)
    setActiveIndex(-1)
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    switch (e.key) {
      case Key.ArrowDown:
        e.preventDefault()
        setOpen(true)
        setActiveIndex((i) => Math.min(i + 1, filtered.length - 1))
        break
      case Key.ArrowUp:
        e.preventDefault()
        setActiveIndex((i) => Math.max(i - 1, 0))
        break
      case Key.Enter:
        if (showList && activeIndex >= 0) {
          e.preventDefault()
          select(filtered[activeIndex])
        }
        break
      case Key.Escape:
        setOpen(false)
        setActiveIndex(-1)
        break
    }
  }

  return (
    <div className="field">
      <label htmlFor={inputId}>{label}</label>
      <div className="combobox">
        <input
          id={inputId}
          type="text"
          role="combobox"
          autoComplete="off"
          aria-expanded={showList}
          aria-controls={listboxId}
          aria-autocomplete="list"
          aria-activedescendant={showList && activeIndex >= 0 ? optionId(id, activeIndex) : undefined}
          value={value}
          disabled={disabled}
          onChange={(e) => {
            onChange(e.target.value)
            setOpen(true)
            setActiveIndex(-1)
          }}
          onFocus={() => setOpen(true)}
          onClick={() => setOpen(true)}
          onBlur={() => {
            setOpen(false)
            setActiveIndex(-1)
          }}
          onKeyDown={handleKeyDown}
        />
        {showList && (
          <ul id={listboxId} role="listbox" className="listbox">
            {filtered.map((option, index) => (
              <li
                key={option.name}
                id={optionId(id, index)}
                role="option"
                aria-selected={index === activeIndex}
                className={index === activeIndex ? 'option active' : 'option'}
                onMouseDown={(e) => {
                  e.preventDefault()
                  select(option)
                }}
                onMouseEnter={() => setActiveIndex(index)}
              >
                <span>{option.name}</span>
                <span className="option-stage">{option.stage}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default Combobox
