import api from './api'
import type {
  BackendAttendanceRecord,
  AttendanceRecord,
} from '../types/attendance'

// ---------------------------------------------------------------------------
// Mapper: snake_case backend → camelCase frontend
// ---------------------------------------------------------------------------

/**
 * Convert a raw backend attendance record into the frontend shape.
 *
 * @param record  Raw backend object.
 * @param labelFn Optional function that resolves an email to a display name
 *                (e.g. from the auth store's staff directory). Falls back to
 *                the raw email when omitted or when no label is found.
 */
export function toAttendanceRecord(
  record: BackendAttendanceRecord,
  labelFn?: (email: string, fallback: string) => string,
): AttendanceRecord {
  return {
    id: String(record.id),
    email: record.email,
    staffName: labelFn ? labelFn(record.email, record.email) : record.email,
    date: record.date,
    checkInAt: record.check_in_at,
    checkOutAt: record.check_out_at ?? undefined,
    hoursWorked: Number(record.hours_worked ?? 0),
    regularHours: Number(record.regular_hours ?? 0),
    overtimeHours: Number(record.overtime_hours ?? 0),
  }
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

export async function fetchAttendanceRecords(params?: {
  skip?: number
  limit?: number
  user_id?: number
  user_email?: string
  date?: string
}) {
  const { data } = await api.get<BackendAttendanceRecord[]>('/attendance', {
    params,
  })
  return Array.isArray(data) ? data : []
}

export async function fetchAttendanceByUserId(
  userId: number,
  params?: { skip?: number; limit?: number },
) {
  const { data } = await api.get<BackendAttendanceRecord[]>(
    `/attendance/user/${userId}`,
    { params },
  )
  return Array.isArray(data) ? data : []
}

export async function fetchAttendanceByEmail(
  email: string,
  params?: { skip?: number; limit?: number },
) {
  const { data } = await api.get<BackendAttendanceRecord[]>(
    `/attendance/user/email/${encodeURIComponent(email)}`,
    { params },
  )
  return Array.isArray(data) ? data : []
}

export async function checkIn(payload: {
  lat: number | null
  lng: number | null
  accuracy: number | null
}) {
  const { data } = await api.post<BackendAttendanceRecord>(
    '/attendance/check-in',
    payload,
  )
  return data
}

export async function checkOut(payload: {
  lat: number | null
  lng: number | null
  accuracy: number | null
}) {
  const { data } = await api.post<BackendAttendanceRecord>(
    '/attendance/check-out',
    payload,
  )
  return data
}

export async function fetchAttendanceRecord(recordId: number) {
  const { data } = await api.get<BackendAttendanceRecord>(
    `/attendance/${recordId}`,
  )
  return data
}
