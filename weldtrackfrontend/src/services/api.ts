import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10_000,
  withCredentials: true, // Send cookies with requests
})

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('weldtrack-auth')
  if (token) {
    try {
      const authData = JSON.parse(token)
      if (authData.token) {
        config.headers.Authorization = `Bearer ${authData.token}`
      }
    } catch {
      // Invalid token format, skip
    }
  }
  return config
})

export default api

