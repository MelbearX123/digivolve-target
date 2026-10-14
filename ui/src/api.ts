// Vite proxies /api/* to the FastAPI server (see vite.config.ts).
export const ApiRoute = {
  Digimon: '/api/digimon',
  Path: '/api/path',
} as const

export type ApiRoute = (typeof ApiRoute)[keyof typeof ApiRoute]

export const ABORT_ERROR = 'AbortError'
