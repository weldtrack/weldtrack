import { defineStore } from 'pinia'
import {
  loginApi,
  fetchCurrentUserApi,
  sendVerificationCodeApi,
  signupApi,
  confirmVerificationCodeApi,
  fetchStaffDirectoryApi,
  resetPasswordApi,
} from '../api/auth'
import type {
  StaffDirectoryEntry,
  StoredAuthState,
  UserRead,
} from '../types/auth'

const AUTH_STORAGE_KEY = 'weldtrack-auth'

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
      email?: string
      role?: string
      isLoggedIn?: boolean
      user?: UserRead
    }
  } catch {
    return null
  }
}

function writeAuthState(state: StoredAuthState & { user?: UserRead }) {
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
    email: readAuthState()?.email || '',
    role: readAuthState()?.role || 'customer',
    isLoggedIn: readAuthState()?.isLoggedIn || false,
    user: readAuthState()?.user as UserRead | undefined,
    staffDirectory: [] as StaffDirectoryEntry[],
    // Runtime-only flag. Persisting this would let a stale browser session skip
    // the server check after a reload.
    sessionValidated: false,
  }),
  actions: {
    async login(payload: { email: string; password: string }) {
      const data = await loginApi(payload)

      this.setSession({
        email: data.user?.email || payload.email,
        role: data.user?.role || 'customer',
        user: data.user,
      })
      this.sessionValidated = true

      return data
    },

    async validateSession() {
      try {
        const user = await fetchCurrentUserApi()
        this.email = user.email
        this.role = user.role
        this.user = user
        this.isLoggedIn = true
        writeAuthState({
          email: this.email,
          role: this.role,
          isLoggedIn: true,
          user: this.user,
        })
        return true
      } catch {
        this.email = ''
        this.role = 'customer'
        this.user = undefined
        this.isLoggedIn = false
        clearAuthState()
        return false
      } finally {
        this.sessionValidated = true
      }
    },

    async sendVerificationCode(email: string) {
      return await sendVerificationCodeApi(email)
    },

    async signup(payload: {
      email: string
      password: string
      role?: string
      full_name?: string
      province?: string
      municipality?: string
      barangay?: string
      house?: string
    }) {
      return await signupApi(payload)
    },

    async confirmVerificationCode(payload: {
      email: string
      code: string
      password?: string
      full_name?: string
      province?: string
      municipality?: string
      barangay?: string
      house?: string
      label?: string
      action: 'changepassword' | 'createaccount'
    }) {
      return await confirmVerificationCodeApi(payload)
    },

    async fetchStaffDirectory() {
      const defaultStaffNames: Record<string, string> = {
        'staff1@weldtrack.com': 'Juan Dela Cruz',
        'staff2@weldtrack.com': 'Marco Santos',
        'staff3@weldtrack.com': 'Ramon Reyes',
        'staff4@weldtrack.com': 'Carlo Mendoza',
        'ramon.reyes@weldtrack.com': 'Ramon Reyes',
        'carlo.mendoza@weldtrack.com': 'Carlo Mendoza',
      }
      const deriveName = (email?: string, fullName?: string) => {
        if (fullName && fullName.trim()) return fullName.trim()
        const lower = (email || '').trim().toLowerCase()
        if (defaultStaffNames[lower]) return defaultStaffNames[lower]
        const local = lower.split('@')[0]?.replace(/[._-]+/g, ' ').trim() || ''
        if (!local) return email || 'Staff Member'
        return local
          .split(/\s+/)
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' ')
      }

      try {
        const data = await fetchStaffDirectoryApi()
        this.staffDirectory = Array.isArray(data)
          ? data.map((user: { id?: string; email?: string; full_name?: string }) => {
              const name = deriveName(user.email, user.full_name)
              return {
                id: String(user.id ?? ''),
                email: user.email || '',
                full_name: name,
                name,
              }
            })
          : []
      } catch (error) {
        this.staffDirectory = []
        const statusCode = (error as { response?: { status?: number } })?.response?.status
        if (statusCode !== 403) throw error
      }

      return this.staffDirectory
    },

    getStaffLabel(staffIdOrEmail: string, fallback = '') {
      const key = String(staffIdOrEmail || '').trim()
      const lower = key.toLowerCase()
      const staff = this.staffDirectory.find(
        (entry) => entry.id === key || entry.email.toLowerCase() === lower,
      )
      if (staff?.full_name) return staff.full_name
      if (staff?.name) return staff.name
      if (staff?.email) return staff.email
      const defaultStaffNames: Record<string, string> = {
        'staff1@weldtrack.com': 'Juan Dela Cruz',
        'staff2@weldtrack.com': 'Marco Santos',
        'staff3@weldtrack.com': 'Ramon Reyes',
        'staff4@weldtrack.com': 'Carlo Mendoza',
        'ramon.reyes@weldtrack.com': 'Ramon Reyes',
        'carlo.mendoza@weldtrack.com': 'Carlo Mendoza',
      }
      if (defaultStaffNames[lower]) return defaultStaffNames[lower]
      if (fallback) {
        const fbLower = fallback.trim().toLowerCase()
        if (defaultStaffNames[fbLower]) return defaultStaffNames[fbLower]
        return fallback
      }
      return ''
    },

    async resetPassword(payload: { email: string; code: string; password: string; password_confirmation?: string; passwordConfirmation?: string; confirm?: string }) {
      return await resetPasswordApi(payload)
    },

    setSession(payload: {
      email?: string
      role?: string
      user?: UserRead
    }) {
      this.role = payload.role || 'customer'
      this.email = payload.email || ''
      this.isLoggedIn = true
      this.user = payload.user
      this.sessionValidated = true

      writeAuthState({
        email: this.email,
        role: this.role,
        isLoggedIn: this.isLoggedIn,
        user: this.user,
      })
    },
    logout() {
      this.email = ''
      this.role = 'customer'
      this.isLoggedIn = false
      this.user = undefined
      this.staffDirectory = []
      this.sessionValidated = true

      clearAuthState()
    },
  },
})
