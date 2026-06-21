import { defineStore } from 'pinia'
import axios from 'axios'
import type { StaffContributionSnapshot } from '../types/staffContributions'
import * as staffContributionService from '../api/staffContributions'

export const useStaffContributionsStore = defineStore('staff-contributions', {
  state: () => ({
    snapshots: [] as StaffContributionSnapshot[],
  }),
  actions: {
    async fetchSnapshots() {
      try {
        this.snapshots = await staffContributionService.fetchSnapshots()
        return this.snapshots
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.snapshots = []
          return this.snapshots
        }
        throw error
      }
    },
  },
})
