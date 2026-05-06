import type { AxiosInstance } from 'axios'

export type VerificationCodePayload = Record<string, string>

export type VerificationCodeResponse = {
  success?: boolean
  token?: string
  email?: string
  role?: string
}

export function requestEmailCode(
  authApi: AxiosInstance,
  payload: VerificationCodePayload,
) {
  return authApi.post<VerificationCodeResponse>('/auth/verifyemail', payload)
}

export function verifyEmailCode(
  authApi: AxiosInstance,
  payload: VerificationCodePayload & { action: 'changepassword' | 'createaccount' },
) {
  return authApi.post<VerificationCodeResponse>('/auth/verifycode', payload)
}