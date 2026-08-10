export interface StaffContributionSnapshot {
  id: string
  taskId: string
  bookingId: string | null
  projectName: string
  taskTitle: string
  contributorIds: string[]
  contributorEmails: string[]
  completedAt: string
}

export type BackendStaffContributionSnapshot = {
  id: string
  taskId: string
  bookingId?: string | null
  projectName: string
  taskTitle: string
  contributorIds?: string[]
  contributorEmails?: string[]
  completedAt: string
}
