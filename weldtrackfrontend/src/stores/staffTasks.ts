import { defineStore } from 'pinia'

export type TaskStatus = 'pending' | 'in-progress' | 'done'

export interface StaffTask {
  id: string
  projectName: string
  title: string
  description: string
  assignedStaffIds: string[]
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

const STAFF_TASKS_STORAGE_KEY = 'weldtrack-staff-tasks'

function readStaffTasks() {
  if (typeof window === 'undefined') {
    return [] as StaffTask[]
  }

  const raw = window.localStorage.getItem(STAFF_TASKS_STORAGE_KEY)
  if (!raw) {
    return [] as StaffTask[]
  }

  try {
    const parsed = JSON.parse(raw) as Array<StaffTask & { assignedStaffId?: string }>
    return parsed.map((task) => ({
      ...task,
      assignedStaffIds: Array.isArray(task.assignedStaffIds)
        ? task.assignedStaffIds
        : task.assignedStaffId
          ? [task.assignedStaffId]
          : [],
    }))
  } catch {
    return [] as StaffTask[]
  }
}

const DEFAULT_TASKS: StaffTask[] = [
  {
    id: `sample-${Date.now()}`,
    projectName: 'Sample Project - Gate Fabrication',
    title: 'Welding and Assembly',
    description: 'Install gate frame and weld panels. Use welding electrodes and cutting discs as needed.',
    assignedStaffIds: ['1', '2'],
    assignedAt: new Date().toISOString(),
    dueDate: '2026-05-10',
    status: 'in-progress',
    location: {
      country: 'PH',
      region: 'Bicol Region (Region V)',
      province: 'Naga',
      municipality: 'Naga City',
      barangay: 'Centro',
      house: '123 Sample St',
    },
  },
]

function writeStaffTasks(tasks: StaffTask[]) {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(STAFF_TASKS_STORAGE_KEY, JSON.stringify(tasks))
}

export const useStaffTasksStore = defineStore('staff-tasks', {
  state: () => ({
    tasks: ((): StaffTask[] => {
      const existing = readStaffTasks()
      if (existing && existing.length > 0) return existing
      // seed with an example task for easier testing
      try {
        writeStaffTasks(DEFAULT_TASKS)
      } catch {}
      return DEFAULT_TASKS
    })(),
  }),
  actions: {
    assignTask(payload: {
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
      const newTask: StaffTask = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        projectName: payload.projectName,
        title: payload.title,
        description: payload.description,
        assignedStaffIds: payload.assignedStaffIds,
        assignedAt: new Date().toISOString(),
        dueDate: payload.dueDate,
        status: 'pending',
        location: {
          country: 'PH',
          region: 'Bicol Region (Region V)',
          province: payload.location.province,
          municipality: payload.location.municipality,
          barangay: payload.location.barangay,
          house: payload.location.house,
        },
      }

      this.tasks.unshift(newTask)
      writeStaffTasks(this.tasks)
    },

    updateTaskStatus(taskId: string, status: TaskStatus) {
      const task = this.tasks.find((item) => item.id === taskId)
      if (!task) return

      task.status = status
      writeStaffTasks(this.tasks)
    },

    removeTask(taskId: string) {
      this.tasks = this.tasks.filter((item) => item.id !== taskId)
      writeStaffTasks(this.tasks)
    },
  },
})
