import { defineStore } from 'pinia'
import api from '../services/api'
import { requestEmailCode, verifyEmailCode } from '../services/emailAuth'

const AUTH_STORAGE_KEY = 'weldtrack-auth'

type StaffDirectoryEntry = {
  id: string
  email: string
}

function readAuthState() {
  if (typeof window === 'undefined') {
    return null
  }

  const storedValue = window.localStorage.getItem(AUTH_STORAGE_KEY)
  if (!storedValue) {
    return null
  }

  try {
    return JSON.parse(storedValue) as {
      token?: string
      email?: string
      role?: string
      isLoggedIn?: boolean
    }
  } catch {
    return null
  }
}

function writeAuthState(state: {
  token: string
  email: string
  role: string
  isLoggedIn: boolean
}) {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(state))
}

function clearAuthState() {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.removeItem(AUTH_STORAGE_KEY)
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: readAuthState()?.token || '',
    email: readAuthState()?.email || '',
    role: readAuthState()?.role || 'customer',
    isLoggedIn: readAuthState()?.isLoggedIn || false,
    staffDirectory: [] as StaffDirectoryEntry[],
  }),
  actions: {
    async login(payload: { email: string; password: string }) {
      const { data } = await api.post('/auth/login', {
        email: payload.email,
        password: payload.password,
      })

      this.setSession({
        token: data.access_token || '',
        email: data.user?.email || payload.email,
        role: data.user?.role || 'customer',
      })

      return data as {
        success?: boolean
        access_token?: string
        user?: {
          id?: number
          email?: string
          role?: string
        }
      }
    },

    async sendVerificationCode(email: string) {
      const { data } = await requestEmailCode(api, { email })
      return data as { success?: boolean }
    },

    async signup(payload: { email: string; password: string; role?: string }) {
      const body: Record<string, string> = {
        email: payload.email,
        password: payload.password,
      }
      if (payload.role) body.role = payload.role

      const { data } = await api.post('/auth/signup', body)
      return data as { success?: boolean }
    },

    async confirmVerificationCode(payload: { email: string; code: string; password?: string; action: 'changepassword' | 'createaccount' }) {
      const { data } = await verifyEmailCode(api, payload)
      return data as { 
        success?: boolean
        token?: string
        email?: string
        role?: string
        access_token?: string
        user?: {
          id?: number
          email?: string
          role?: string
        }
      }
    },

    async fetchStaffDirectory() {
      try {
        const { data } = await api.get('/auth/staff')
        this.staffDirectory = Array.isArray(data)
          ? data.map((user: { id?: number; email?: string }) => ({
              id: String(user.id ?? ''),
              email: user.email || '',
            }))
          : []
      } catch (error) {
        this.staffDirectory = []
        const statusCode = (error as { response?: { status?: number } })?.response?.status
        if (statusCode !== 403) throw error
      }

      return this.staffDirectory
    },

    getStaffLabel(staffId: string, fallback = '') {
      const staff = this.staffDirectory.find((entry) => entry.id === String(staffId))
      if (staff?.email) return staff.email
      if (fallback) return fallback
      return ''
    },

    async resetPassword(payload: { email: string; code: string; password: string; password_confirmation?: string; passwordConfirmation?: string; confirm?: string }) {
      // Normalize common confirmation field names to `password_confirmation` for backend compatibility
      const body: Record<string, string> = {
        email: payload.email,
        code: payload.code,
        password: payload.password,
        password_confirmation: payload.password_confirmation || payload.passwordConfirmation || payload.confirm || '',
      }

      const { data } = await api.post('/auth/forgot-password/reset', body)
      return data as { success?: boolean }
    },

    setSession(payload: {
      token?: string
      email?: string
      role?: string
    }) {
      this.token = payload.token || ''
      this.role = payload.role || 'customer'
      this.email = payload.email || ''
      this.isLoggedIn = true

      writeAuthState({
        token: this.token,
        email: this.email,
        role: this.role,
        isLoggedIn: this.isLoggedIn,
      })
    },
    logout() {
      this.token = ''
      this.email = ''
      this.role = 'customer'
      this.isLoggedIn = false
      this.staffDirectory = []

      clearAuthState()
    },
  },
})
