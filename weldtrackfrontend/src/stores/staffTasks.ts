import { defineStore } from 'pinia'
import api from '../services/api'

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

type BackendStaffTask = {
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

function toStaffTask(task: BackendStaffTask): StaffTask {
  return {
    id: task.id,
    bookingId: task.bookingId ?? null,
    projectName: task.projectName,
    title: task.title,
    description: task.description ?? '',
    assignedStaffIds: Array.isArray(task.assignedStaffIds) ? task.assignedStaffIds.map(String) : [],
    assignedStaffEmails: Array.isArray(task.assignedStaffEmails) ? task.assignedStaffEmails.filter(Boolean) : [],
    assignedAt: task.assignedAt,
    dueDate: task.dueDate,
    status: task.status,
    location: {
      country: task.location.country ?? 'PH',
      region: task.location.region ?? 'Bicol Region (Region V)',
      province: task.location.province,
      municipality: task.location.municipality,
      barangay: task.location.barangay,
      house: task.location.house,
    },
  }
}

export const useStaffTasksStore = defineStore('staff-tasks', {
  state: () => ({
    tasks: [] as StaffTask[],
  }),
  actions: {
    async fetchTasks(params?: { status?: TaskStatus }) {
      const { data } = await api.get<BackendStaffTask[]>('/staff-tasks', {
        params: {
          status: params?.status,
        },
      })

      this.tasks = Array.isArray(data) ? data.map(toStaffTask) : []
      return this.tasks
    },

    async assignTask(payload: {
      bookingId?: number | null
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
      const { data } = await api.post<BackendStaffTask>('/staff-tasks', {
        bookingId: payload.bookingId ?? null,
        projectName: payload.projectName,
        title: payload.title,
        description: payload.description,
        assignedStaffIds: payload.assignedStaffIds.map((id) => Number(id)),
        dueDate: payload.dueDate,
        location: {
          province: payload.location.province,
          municipality: payload.location.municipality,
          barangay: payload.location.barangay,
          house: payload.location.house,
        },
      })

      const created = toStaffTask(data)
      this.tasks.unshift(created)
      return created
    },

    async updateTaskStatus(taskId: string, status: TaskStatus) {
      const { data } = await api.put<BackendStaffTask>(`/staff-tasks/${taskId}/status`, { status })
      const updated = toStaffTask(data)
      const index = this.tasks.findIndex((item) => item.id === taskId)
      if (index !== -1) {
        this.tasks[index] = updated
      }
      return updated
    },

    async removeTask(taskId: string) {
      await api.delete(`/staff-tasks/${taskId}`)
      this.tasks = this.tasks.filter((item) => item.id !== taskId)
    },
  },
})
