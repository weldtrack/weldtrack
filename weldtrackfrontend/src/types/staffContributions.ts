export interface StaffContributionSnapshot {
  id: string
  taskId: string
  bookingId: number | null
  projectName: string
  taskTitle: string
  contributorIds: string[]
  contributorEmails: string[]
  completedAt: string
}

export type BackendStaffContributionSnapshot = {
  id: number
  taskId: string
  bookingId?: number | null
  projectName: string
  taskTitle: string
  contributorIds?: number[]
  contributorEmails?: string[]
  completedAt: string
}
