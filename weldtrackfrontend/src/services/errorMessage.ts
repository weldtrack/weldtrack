import axios from 'axios'

const GENERIC_BACKEND_ERROR_MESSAGE = 'Something went wrong. Try again later.'

const SERVER_FAILURE_HINTS = [
  'internal server error',
  'server error',
  'database',
  'db error',
  'sql',
  'sqlite',
  'postgres',
  'psycopg',
  'operationalerror',
  'traceback',
]

function pickMessage(data: unknown): string | undefined {
  if (typeof data === 'string') {
    const message = data.trim()
    return message || undefined
  }

  if (data && typeof data === 'object') {
    const payload = data as {
      message?: unknown
      detail?: unknown
      error?: unknown
    }

    if (typeof payload.message === 'string' && payload.message.trim()) {
      return payload.message.trim()
    }

    if (typeof payload.detail === 'string' && payload.detail.trim()) {
      return payload.detail.trim()
    }

    if (typeof payload.error === 'string' && payload.error.trim()) {
      return payload.error.trim()
    }
  }

  return undefined
}

function looksLikeServerFailure(message?: string): boolean {
  if (!message) return false
  const normalized = message.toLowerCase()
  return SERVER_FAILURE_HINTS.some((hint) => normalized.includes(hint))
}

export function getUserFriendlyApiError(error: unknown, fallback: string = GENERIC_BACKEND_ERROR_MESSAGE): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const responseMessage = pickMessage(error.response?.data)

    if (
      !error.response
      || (typeof status === 'number' && status >= 500)
      || error.code === 'ECONNABORTED'
      || looksLikeServerFailure(responseMessage)
    ) {
      return GENERIC_BACKEND_ERROR_MESSAGE
    }

    if (responseMessage) {
      return responseMessage
    }

    if (typeof error.response?.statusText === 'string' && error.response.statusText.trim()) {
      return error.response.statusText
    }

    return fallback
  }

  if (error instanceof Error) {
    if (looksLikeServerFailure(error.message)) {
      return GENERIC_BACKEND_ERROR_MESSAGE
    }

    const message = error.message.trim()
    return message || fallback
  }

  return fallback
}

export { GENERIC_BACKEND_ERROR_MESSAGE }
