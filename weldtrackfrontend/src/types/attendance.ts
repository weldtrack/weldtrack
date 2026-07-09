/**
 * Shape returned by the backend (snake_case, raw types).
 * Maps to `AttendanceResponse` from `app/schemas/attendance.py`.
 */
export interface BackendAttendanceRecord {
  id: number
  email: string
  date: string
  check_in_at: string
  check_out_at: string | null
  hours_worked: number
  regular_hours: number
  overtime_hours: number
}

/** Frontend-friendly shape (camelCase). */
export interface AttendanceRecord {
  id: string
  email: string
  staffName: string
  date: string
  checkInAt: string
  checkOutAt?: string
  hoursWorked: number
  regularHours: number
  overtimeHours: number
}

/**
 * Shape returned by `GET /settings/attendance-location`.
 * Maps to `AttendanceSiteResponse` from `app/schemas/settings.py`.
 */
export interface BackendAttendanceSite {
  lat: number
  lng: number
  radius_meters: number
  updated_at: string
}

/** Frontend-friendly shape. */
export interface AttendanceSite {
  lat: number
  lng: number
  radiusMeters: number
  updatedAt: string
}
