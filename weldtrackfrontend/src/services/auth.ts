import api from './api'
import { requestEmailCode, verifyEmailCode } from './emailAuth'
import type {
  LoginPayload,
  LoginResponse,
  SignupPayload,
  SignupResponse,
  ConfirmVerificationPayload,
  ConfirmVerificationResponse,
  ResetPasswordPayload,
  ResetPasswordResponse,
  SendVerificationCodeResponse,
} from '../types/auth'

export async function loginApi(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', {
    email: payload.email,
    password: payload.password,
  })
  return data
}

export async function sendVerificationCodeApi(email: string): Promise<SendVerificationCodeResponse> {
  const { data } = await requestEmailCode(api, { email })
  return data
}

export async function signupApi(payload: SignupPayload): Promise<SignupResponse> {
  const body: Record<string, string> = {
    email: payload.email,
    password: payload.password,
  }
  if (payload.role) body.role = payload.role

  const { data } = await api.post<SignupResponse>('/auth/signup', body)
  return data
}

export async function confirmVerificationCodeApi(payload: ConfirmVerificationPayload): Promise<ConfirmVerificationResponse> {
  const { data } = await verifyEmailCode(api, payload)
  return data
}

export async function fetchStaffDirectoryApi() {
  const { data } = await api.get('/auth/staff')
  return data
}

export async function resetPasswordApi(payload: ResetPasswordPayload): Promise<ResetPasswordResponse> {
  const body: Record<string, string> = {
    email: payload.email,
    code: payload.code,
    password: payload.password,
    password_confirmation: payload.password_confirmation || payload.passwordConfirmation || payload.confirm || '',
  }

  const { data } = await api.post<ResetPasswordResponse>('/auth/forgot-password/reset', body)
  return data
}
