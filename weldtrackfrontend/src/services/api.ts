import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { useLoadingStore } from '../stores/loading'

type TrackedRequestConfig = InternalAxiosRequestConfig & {
  __loadingTracked?: boolean
  skipGlobalLoading?: boolean
}

function startGlobalLoading(config: TrackedRequestConfig) {
  if (config.skipGlobalLoading) {
    return
  }
  const loadingStore = useLoadingStore()
  loadingStore.start()
  config.__loadingTracked = true
}

function finishGlobalLoading(config?: TrackedRequestConfig) {
  if (!config?.__loadingTracked) {
    return
  }

  const loadingStore = useLoadingStore()
  loadingStore.finish()
  config.__loadingTracked = false
}

function getStoredAuthToken() {
  if (typeof window === 'undefined') {
    return ''
  }

  const storedValue = window.localStorage.getItem('weldtrack-auth')
  if (!storedValue) {
    return ''
  }

  try {
    const parsed = JSON.parse(storedValue) as { token?: string }
    return parsed.token || ''
  } catch {
    return ''
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10_000,
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const trackedConfig = config as TrackedRequestConfig
  startGlobalLoading(trackedConfig)

  // Skip auth token for login/signup endpoints (they don't need it and stale tokens can cause issues)
  const url = trackedConfig.url || ''
  const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/signup') || url.includes('/auth/verifycode') || url.includes('/auth/verifyemail')
  
  if (!isAuthEndpoint) {
    const token = getStoredAuthToken()
    if (token) {
      trackedConfig.headers = trackedConfig.headers ?? {}
      const headers = trackedConfig.headers as Record<string, string>
      if (!headers.Authorization) {
        headers.Authorization = `Bearer ${token}`
      }
    }
  }

  return trackedConfig
}, (error) => {
  finishGlobalLoading(error?.config as TrackedRequestConfig | undefined)
  return Promise.reject(error)
})

api.interceptors.response.use((response) => {
  finishGlobalLoading(response.config as TrackedRequestConfig)
  return response
}, (error) => {
  finishGlobalLoading(error?.config as TrackedRequestConfig | undefined)
  
  if (error?.response?.status === 401) {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('weldtrack-auth')
    }
  }
  
  return Promise.reject(error)
})

export default api

