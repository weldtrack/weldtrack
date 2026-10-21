import api from './api'
import { requestEmailCode, verifyEmailCode } from '../services/emailAuth'
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
  UserRead,
} from '../types/auth'

export async function loginApi(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', {
    email: payload.email,
    password: payload.password,
  })
  return data
}

export async function fetchCurrentUserApi(): Promise<UserRead> {
  const { data } = await api.get<UserRead>('/auth/me')
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
  if (payload.full_name) body.full_name = payload.full_name
  if (payload.province) body.province = payload.province
  if (payload.municipality) body.municipality = payload.municipality
  if (payload.barangay) body.barangay = payload.barangay
  if (payload.house) body.house = payload.house

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
