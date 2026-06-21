export interface StaffDirectoryEntry {
  id: string
  email: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface LoginResponse {
  success?: boolean
  access_token?: string
  user?: {
    id?: number
    email?: string
    role?: string
  }
}

export interface SignupPayload {
  email: string
  password: string
  role?: string
}

export interface SignupResponse {
  success?: boolean
}

export type ConfirmVerificationPayload = {
  email: string
  code: string
  password?: string
  action: 'changepassword' | 'createaccount'
}

export interface ConfirmVerificationResponse {
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

export interface ResetPasswordPayload {
  email: string
  code: string
  password: string
  password_confirmation?: string
  passwordConfirmation?: string
  confirm?: string
}

export interface ResetPasswordResponse {
  success?: boolean
}

export interface SendVerificationCodeResponse {
  success?: boolean
}

export interface StoredAuthState {
  token: string
  email: string
  role: string
  isLoggedIn: boolean
}
