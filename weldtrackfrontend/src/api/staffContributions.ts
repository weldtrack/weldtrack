import api from './api'
import type { StaffContributionSnapshot, BackendStaffContributionSnapshot } from '../types/staffContributions'

export function toSnapshot(snapshot: BackendStaffContributionSnapshot): StaffContributionSnapshot {
  return {
    id: String(snapshot.id),
    taskId: snapshot.taskId,
    bookingId: snapshot.bookingId ?? null,
    projectName: snapshot.projectName,
    taskTitle: snapshot.taskTitle,
    contributorIds: Array.isArray(snapshot.contributorIds) ? snapshot.contributorIds.map(String) : [],
    contributorEmails: Array.isArray(snapshot.contributorEmails) ? snapshot.contributorEmails.filter(Boolean) : [],
    completedAt: snapshot.completedAt,
  }
}

export async function fetchSnapshots() {
  const { data } = await api.get<BackendStaffContributionSnapshot[]>('/staff-contributions', {
    params: { limit: 500 },
  })
  return Array.isArray(data) ? data.map(toSnapshot) : []
}
