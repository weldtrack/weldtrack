import api from './api'
import type { BackendAttendanceSite, AttendanceSite } from '../types/attendance'

// ---------------------------------------------------------------------------
// Mapper
// ---------------------------------------------------------------------------

export function toAttendanceSite(raw: BackendAttendanceSite): AttendanceSite {
  return {
    lat: raw.lat,
    lng: raw.lng,
    radiusMeters: raw.radius_meters,
    updatedAt: raw.updated_at,
  }
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

/**
 * Fetch the currently configured attendance site (geofence).
 * Returns `null` when the admin hasn't set one yet (404).
 */
export async function fetchAttendanceLocation(): Promise<AttendanceSite | null> {
  try {
    const { data } = await api.get<BackendAttendanceSite>(
      '/settings/attendance-location',
    )
    return toAttendanceSite(data)
  } catch (err: any) {
    if (err?.response?.status === 404) return null
    throw err
  }
}

/**
 * Create or update the attendance site (admin only).
 */
export async function setAttendanceLocation(payload: {
  lat: number
  lng: number
  radius_meters: number
}) {
  const { data } = await api.post<BackendAttendanceSite>(
    '/settings/attendance-location',
    payload,
  )
  return toAttendanceSite(data)
}
