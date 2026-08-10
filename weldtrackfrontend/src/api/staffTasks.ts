import api from './api'
import type { StaffTask, BackendStaffTask, TaskStatus } from '../types/staffTasks'

export function toStaffTask(task: BackendStaffTask): StaffTask {
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

export async function fetchTasks(params?: { status?: TaskStatus }) {
  const { data } = await api.get<BackendStaffTask[]>('/staff-tasks', {
    params: {
      status: params?.status,
    },
  })

  return Array.isArray(data) ? data.map(toStaffTask) : []
}

export async function assignTask(payload: {
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
  const { data } = await api.post<BackendStaffTask>('/staff-tasks', {
    bookingId: payload.bookingId ?? null,
    projectName: payload.projectName,
    title: payload.title,
    description: payload.description,
    assignedStaffIds: payload.assignedStaffIds,
    dueDate: payload.dueDate,
    location: {
      province: payload.location.province,
      municipality: payload.location.municipality,
      barangay: payload.location.barangay,
      house: payload.location.house,
    },
  })

  return toStaffTask(data)
}

export async function updateTaskStatus(taskId: string, status: TaskStatus) {
  const { data } = await api.put<BackendStaffTask>(`/staff-tasks/${taskId}/status`, { status })
  return toStaffTask(data)
}

export async function removeTask(taskId: string) {
  await api.delete(`/staff-tasks/${taskId}`)
}
