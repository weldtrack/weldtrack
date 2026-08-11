export type AttendanceAction = 'morning-in' | 'morning-out' | 'afternoon-in' | 'afternoon-out'
export type AttendanceStatus = 'Incomplete' | 'Completed'
export type ArrivalStatus = 'On Time' | 'Late'

export interface BackendAttendanceRecord {
  id: string
  email: string
  date: string
  check_in_at: string | null
  check_out_at: string | null
  morning_in_at: string | null
  morning_out_at: string | null
  afternoon_in_at: string | null
  afternoon_out_at: string | null
  morning_hours: number
  afternoon_hours: number
  total_hours_worked: number
  hours_worked: number
  regular_hours: number
  overtime_hours: number
  arrival_status: ArrivalStatus | null
  attendance_status: AttendanceStatus
  next_action: AttendanceAction | null
  next_action_available: boolean
  next_action_available_at: string | null
  next_action_message: string
  attendance_date: string
  timezone: string
  manually_modified: boolean
  correction_note: string | null
  corrected_at: string | null
  corrected_by_email: string | null
}

export interface AttendanceRecord {
  id: string
  email: string
  staffName: string
  date: string
  morningInAt?: string
  morningOutAt?: string
  afternoonInAt?: string
  afternoonOutAt?: string
  morningHours: number
  afternoonHours: number
  totalHoursWorked: number
  regularHours: number
  overtimeHours: number
  arrivalStatus?: ArrivalStatus
  attendanceStatus: AttendanceStatus
  nextAction?: AttendanceAction
  nextActionAvailable: boolean
  nextActionAvailableAt?: string
  nextActionMessage: string
  timezone: string
  manuallyModified: boolean
  correctionNote?: string
  correctedAt?: string
  correctedByEmail?: string
}

export interface AttendanceDayState {
  attendance_date: string
  timezone: string
  next_action: AttendanceAction | null
  next_action_available: boolean
  next_action_available_at: string | null
  next_action_message: string
  record: BackendAttendanceRecord | null
}

export interface BackendAttendanceSite {
  lat: number
  lng: number
  radius_meters: number
  updated_at: string
}

export interface AttendanceSite {
  lat: number
  lng: number
  radiusMeters: number
  updatedAt: string
}
