import api from './api'
import type { AttendanceAction, AttendanceDayState, AttendanceRecord, BackendAttendanceRecord } from '../types/attendance'

export function toAttendanceRecord(
  record: BackendAttendanceRecord,
  labelFn?: (email: string, fallback: string) => string,
): AttendanceRecord {
  return {
    id: String(record.id),
    email: record.email,
    staffName: labelFn ? labelFn(record.email, record.email) : record.email,
    date: record.date,
    morningInAt: record.morning_in_at || undefined,
    morningOutAt: record.morning_out_at || undefined,
    afternoonInAt: record.afternoon_in_at || undefined,
    afternoonOutAt: record.afternoon_out_at || undefined,
    morningHours: Number(record.morning_hours ?? 0),
    afternoonHours: Number(record.afternoon_hours ?? 0),
    totalHoursWorked: Number(record.total_hours_worked ?? record.hours_worked ?? 0),
    regularHours: Number(record.regular_hours ?? 0),
    overtimeHours: Number(record.overtime_hours ?? 0),
    arrivalStatus: record.arrival_status || undefined,
    attendanceStatus: record.attendance_status,
    nextAction: record.next_action || undefined,
    nextActionAvailable: record.next_action_available,
    nextActionAvailableAt: record.next_action_available_at || undefined,
    nextActionMessage: record.next_action_message,
    timezone: record.timezone,
    manuallyModified: record.manually_modified,
    correctionNote: record.correction_note || undefined,
    correctedAt: record.corrected_at || undefined,
    correctedByEmail: record.corrected_by_email || undefined,
  }
}

export async function fetchAttendanceRecords(params?: { skip?: number; limit?: number; user_id?: string; user_email?: string; date?: string }) {
  const { data } = await api.get<BackendAttendanceRecord[]>('/attendance', { params })
  return Array.isArray(data) ? data : []
}

export async function fetchTodayAttendance() {
  const { data } = await api.get<BackendAttendanceRecord[]>('/attendance/today')
  return Array.isArray(data) ? data : []
}

export async function fetchTodayAttendanceState() {
  const { data } = await api.get<AttendanceDayState>('/attendance/state/today')
  return data
}

export async function submitAttendanceAction(action: AttendanceAction, payload: { lat: number; lng: number; accuracy: number }) {
  const { data } = await api.post<BackendAttendanceRecord>(`/attendance/${action}`, payload)
  return data
}

export async function correctAttendance(recordId: string, payload: {
  morning_in_at?: string
  morning_out_at?: string
  afternoon_in_at?: string
  afternoon_out_at?: string
  reason: string
}) {
  const { data } = await api.patch<BackendAttendanceRecord>(`/attendance/${recordId}/correction`, payload)
  return data
}

export async function fetchAttendanceByUserId(userId: string, params?: { skip?: number; limit?: number }) {
  const { data } = await api.get<BackendAttendanceRecord[]>(`/attendance/user/${userId}`, { params })
  return Array.isArray(data) ? data : []
}

export async function fetchAttendanceByEmail(email: string, params?: { skip?: number; limit?: number }) {
  const { data } = await api.get<BackendAttendanceRecord[]>(`/attendance/user/email/${encodeURIComponent(email)}`, { params })
  return Array.isArray(data) ? data : []
}

export async function fetchAttendanceRecord(recordId: string) {
  const { data } = await api.get<BackendAttendanceRecord>(`/attendance/${recordId}`)
  return data
}
