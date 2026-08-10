export type PayslipStatus = 'draft' | 'approved' | 'paid'
export type MoneyValue = number | string

export interface Payslip {
  id: string
  staff_id: string
  staff_email: string
  period_start: string
  period_end: string
  regular_hours: MoneyValue
  overtime_hours: MoneyValue
  hourly_rate: MoneyValue
  overtime_rate: MoneyValue
  regular_pay: MoneyValue
  overtime_pay: MoneyValue
  allowances: MoneyValue
  bonuses: MoneyValue
  deductions: MoneyValue
  gross_pay: MoneyValue
  net_pay: MoneyValue
  notes?: string | null
  status: PayslipStatus
  created_by_id?: string | null
  created_at: string
  updated_at: string
}

export interface PayslipCreatePayload {
  staff_id: string
  period_start: string
  period_end: string
  hourly_rate: number
  overtime_rate?: number | null
  allowances: number
  bonuses: number
  deductions: number
  notes?: string | null
}
