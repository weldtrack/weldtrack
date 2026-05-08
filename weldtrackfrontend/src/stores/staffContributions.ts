import { defineStore } from 'pinia'
import api from '../services/api'

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

type BackendStaffContributionSnapshot = {
  id: number
  taskId: string
  bookingId?: number | null
  projectName: string
  taskTitle: string
  contributorIds?: number[]
  contributorEmails?: string[]
  completedAt: string
}

function toSnapshot(snapshot: BackendStaffContributionSnapshot): StaffContributionSnapshot {
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

export const useStaffContributionsStore = defineStore('staff-contributions', {
  state: () => ({
    snapshots: [] as StaffContributionSnapshot[],
  }),
  actions: {
    async fetchSnapshots() {
      const { data } = await api.get<BackendStaffContributionSnapshot[]>('/staff-contributions', {
        params: { limit: 500 },
      })
      this.snapshots = Array.isArray(data) ? data.map(toSnapshot) : []
      return this.snapshots
    },
  },
})
