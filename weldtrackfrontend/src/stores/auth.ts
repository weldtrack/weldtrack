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
  }),
  actions: {
    async login(payload: { email: string; password: string }) {
      const data = await loginApi(payload)

      this.setSession({
        email: data.user?.email || payload.email,
        role: data.user?.role || 'customer',
        user: data.user,
      })

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
      }
    },

    async sendVerificationCode(email: string) {
      return await sendVerificationCodeApi(email)
    },

    async signup(payload: { email: string; password: string; role?: string }) {
      return await signupApi(payload)
    },

    async confirmVerificationCode(payload: { email: string; code: string; password?: string; action: 'changepassword' | 'createaccount' }) {
      return await confirmVerificationCodeApi(payload)
    },

    async fetchStaffDirectory() {
      try {
        const data = await fetchStaffDirectoryApi()
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

      clearAuthState()
    },
  },
})
