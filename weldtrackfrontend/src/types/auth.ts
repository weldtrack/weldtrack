export interface UserRead {
  id: number
  email: string
  role: string
  created_at: string
  is_banned: boolean
  is_online: boolean
  last_active?: string
  profile_image?: string
  mobile_phone?: string
}

export interface UserUpdate {
  fullname?: string
  mobile_phone?: string
  profile_image?: string
  email?: string
  password?: string
}

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
  user?: UserRead
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
  user?: UserRead
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
  email: string
  role: string
  isLoggedIn: boolean
}
