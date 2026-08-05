import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { useLoadingStore } from '../stores/loading'

type TrackedRequestConfig = InternalAxiosRequestConfig & {
  __loadingTracked?: boolean
  skipGlobalLoading?: boolean
  useGlobalLoading?: boolean
}

function startGlobalLoading(config: TrackedRequestConfig) {
  // Global loading is opt-in: only track requests where useGlobalLoading === true.
  if (!config?.useGlobalLoading || config.skipGlobalLoading) {
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

function isPublicAuthEndpoint(url: string) {
  return [
    '/auth/login',
    '/auth/signup',
    '/auth/verifycode',
    '/auth/verifyemail',
    '/auth/forgot-password/reset',
  ].some((endpoint) => url.startsWith(endpoint))
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
      const requestUrl = String(error?.config?.url || '')
      const isDashboardPage = window.location.pathname === '/dashboard'
        || window.location.pathname.startsWith('/dashboard/')
      if (!isPublicAuthEndpoint(requestUrl) && isDashboardPage) {
        const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`
        window.location.replace(`/login?redirect=${encodeURIComponent(redirect)}`)
      }
    }
  }

  return Promise.reject(error)
})

export default api
