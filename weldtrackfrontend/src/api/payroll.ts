import api from './api'
import type { Payslip, PayslipCreatePayload, PayslipStatus } from '../types/payroll'

export async function fetchPayslips() {
  const { data } = await api.get<Payslip[]>('/payroll')
  return data
}

export async function fetchMyPayslips() {
  const { data } = await api.get<Payslip[]>('/payroll/mine')
  return data
}

export async function createPayslip(payload: PayslipCreatePayload) {
  const { data } = await api.post<Payslip>('/payroll', payload)
  return data
}

export async function updatePayslipStatus(id: string, status: PayslipStatus) {
  const { data } = await api.patch<Payslip>(`/payroll/${id}/status`, { status })
  return data
}

export async function deletePayslip(id: string) {
  await api.delete(`/payroll/${id}`)
}
