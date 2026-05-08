import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { useLoadingStore } from '../stores/loading'

type TrackedRequestConfig = InternalAxiosRequestConfig & {
  __loadingTracked?: boolean
}

function startGlobalLoading(config: TrackedRequestConfig) {
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

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10_000,
  withCredentials: true, // Send cookies with requests
})

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const trackedConfig = config as TrackedRequestConfig

  const token = localStorage.getItem('weldtrack-auth')
  if (token) {
    try {
      const authData = JSON.parse(token)
      if (authData.token) {
        trackedConfig.headers.Authorization = `Bearer ${authData.token}`
      }
    } catch {
      // Invalid token format, skip
    }
  }
  startGlobalLoading(trackedConfig)
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
  return Promise.reject(error)
})

export default api

