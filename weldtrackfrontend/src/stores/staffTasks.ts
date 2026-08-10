import { defineStore } from 'pinia'
import axios from 'axios'
import type { StaffTask, TaskStatus } from '../types/staffTasks'
import * as staffTaskService from '../api/staffTasks'

export const useStaffTasksStore = defineStore('staff-tasks', {
  state: () => ({
    tasks: [] as StaffTask[],
  }),
  actions: {
    async fetchTasks(params?: { status?: TaskStatus }) {
      try {
        this.tasks = await staffTaskService.fetchTasks(params)
        return this.tasks
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          this.tasks = []
          return this.tasks
        }
        throw error
      }
    },

    async assignTask(payload: {
      bookingId?: string | null
      projectName: string
      title: string
      description: string
      assignedStaffIds: string[]
      dueDate: string
      location: {
        province: string
        municipality: string
        barangay: string
        house: string
      }
    }) {
      const created = await staffTaskService.assignTask(payload)
      this.tasks.unshift(created)
      return created
    },

    async updateTaskStatus(taskId: string, status: TaskStatus) {
      const updated = await staffTaskService.updateTaskStatus(taskId, status)
      const index = this.tasks.findIndex((item) => item.id === taskId)
      if (index !== -1) {
        this.tasks[index] = updated
      }
      return updated
    },

    async removeTask(taskId: string) {
      await staffTaskService.removeTask(taskId)
      this.tasks = this.tasks.filter((item) => item.id !== taskId)
    },
  },
})
