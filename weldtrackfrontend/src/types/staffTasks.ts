export type TaskStatus = 'pending' | 'in-progress' | 'done'

export interface StaffTask {
  id: string
  bookingId: number | null
  projectName: string
  title: string
  description: string
  assignedStaffIds: string[]
  assignedStaffEmails: string[]
  assignedAt: string
  dueDate: string
  status: TaskStatus
  location: {
    country: 'PH'
    region: 'Bicol Region (Region V)'
    province: string
    municipality: string
    barangay: string
    house: string
  }
}

export type BackendStaffTask = {
  id: string
  bookingId?: number | null
  projectName: string
  title: string
  description?: string | null
  assignedStaffIds: number[]
  assignedStaffEmails?: string[]
  assignedAt: string
  dueDate: string
  status: TaskStatus
  location: {
    country?: 'PH'
    region?: 'Bicol Region (Region V)'
    province: string
    municipality: string
    barangay: string
    house: string
  }
}
