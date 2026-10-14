export type Digimon = {
  name: string
  stage: string
}

// Matches the API's Kind enum.
export const Kind = {
  Evolve: 'evolve',
  Devolve: 'devolve',
  Swap: 'swap',
} as const

export type Kind = (typeof Kind)[keyof typeof Kind]

export type Requirements = Record<string, number | string | string[]>

export type Step = {
  to: string
  kind: Kind
  requirements: Requirements
}

export type PathResponse = {
  start: string
  target: string
  steps: Step[]
}
