<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { useAuthStore } from '../../../stores/auth'
import { useStaffTasksStore, type TaskStatus } from '../../../stores/staffTasks'
import { useInventoryStore } from '../../../stores/inventory'
import api from '../../../services/api'
import { useBookingsStore } from '../../../stores/bookings'

interface StaffMember {
  id: string
  name: string
}

const authStore = useAuthStore()
const staffTasksStore = useStaffTasksStore()
const isAdmin = computed(() => authStore.role === 'admin')

const staffList = ref<StaffMember[]>([
  { id: '1', name: 'Juan Cruz' },
  { id: '2', name: 'Maria Santos' },
  { id: '3', name: 'Carlos Reyes' },
  { id: '4', name: 'Rosa Dela Cruz' },
])

const staffCountOptions = [2, 4, 6, 8, 10]

const currentUserId = computed(() => {
  const email = authStore.email?.toLowerCase() || ''

  if (email.includes('juan')) return '1'
  if (email.includes('maria')) return '2'
  if (email.includes('carlos')) return '3'
  if (email.includes('rosa')) return '4'
  return '1'
})

const myAssignedTasks = computed(() => {
  return staffTasksStore.tasks.filter((task) => task.assignedStaffIds.includes(currentUserId.value))
})

const newTaskForm = ref({
  projectName: '',
  title: '',
  description: '',
  requiredStaffCount: 2,
  assignedStaffIds: ['1', '2'] as string[],
  dueDate: '',
  location: {
    country: 'PH' as const,
    region: 'Bicol Region (Region V)' as const,
    province: '',
    municipality: '',
    barangay: '',
    house: '',
  },
})

const inventoryStore = useInventoryStore()

// record materials modal
const isRecordModalOpen = ref(false)
const recordingTask = ref<string | null>(null)
const recordForm = reactive({
  bookingId: '',
  lines: [{ itemId: '', quantity: 1 }] as Array<{ itemId: string; quantity: number }>,
  beforeImageFile: null as File | null,
  afterImageFile: null as File | null,
  beforeImagePreview: '' as string,
  afterImagePreview: '' as string,
})

function openRecordModal(taskId: string) {
  recordingTask.value = taskId
  recordForm.lines = [{ itemId: inventoryStore.items[0]?.id || '', quantity: 1 }]
  recordForm.bookingId = ''
  recordForm.beforeImageFile = null
  recordForm.afterImageFile = null
  recordForm.beforeImagePreview = ''
  recordForm.afterImagePreview = ''
  isRecordModalOpen.value = true
}

function closeRecordModal() {
  isRecordModalOpen.value = false
  recordingTask.value = null
  recordForm.beforeImageFile = null
  recordForm.afterImageFile = null
  recordForm.beforeImagePreview = ''
  recordForm.afterImagePreview = ''
}

function handleBeforeImageChange(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  recordForm.beforeImageFile = file
  if (!file) {
    recordForm.beforeImagePreview = ''
    return
  }
  const reader = new FileReader()
  reader.onload = () => (recordForm.beforeImagePreview = String(reader.result || ''))
  reader.readAsDataURL(file)
}

function handleAfterImageChange(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  recordForm.afterImageFile = file
  if (!file) {
    recordForm.afterImagePreview = ''
    return
  }
  const reader = new FileReader()
  reader.onload = () => (recordForm.afterImagePreview = String(reader.result || ''))
  reader.readAsDataURL(file)
}

function addMaterialLine() {
  recordForm.lines.push({ itemId: inventoryStore.items[0]?.id || '', quantity: 1 })
}

function removeMaterialLine(index: number) {
  if (recordForm.lines.length <= 1) return
  recordForm.lines.splice(index, 1)
}

async function recordMaterialsUsage() {
  if (!recordingTask.value) return
  // bookingId is optional in the UI; validate only if provided
  const bookingIdRaw = (recordForm.bookingId || '').toString().trim()
  let bookingId: number | null = null
  if (bookingIdRaw) {
    const bid = Number(bookingIdRaw)
    if (!Number.isFinite(bid) || bid <= 0) {
      window.alert('Booking ID must be a valid number.')
      return
    }
    bookingId = bid
  }

  const validLines = recordForm.lines.filter((line) => line.itemId && line.quantity > 0)
  if (validLines.length === 0) return

  const taskId = recordingTask.value

  // Require both before and after images to be attached
  if (!recordForm.beforeImagePreview || !recordForm.afterImagePreview) {
    window.alert('Please attach both before and after images before submitting.')
    return
  }

  // Try server submission first; fallback to local stockOut if API unavailable
  try {
    const payload = {
      submittedBy: Number(currentUserId.value) || undefined,
      taskId,
      movementType: 'stock_out',
      lines: validLines.map((l) => ({ itemId: l.itemId, quantity: l.quantity })),
      // include data-urls if available so server can persist, otherwise booking store will be patched locally
      beforeImage: recordForm.beforeImagePreview || undefined,
      afterImage: recordForm.afterImagePreview || undefined,
    }
    const res = await api.post(`/bookings/${bookingId ?? ''}/materials`, payload)
    const materials = res.data.materials ?? res.data

    if (Array.isArray(materials) && materials.length > 0) {
      materials.forEach((m: any) => {
        const itemIdStr = String(m.itemId)
        const item = inventoryStore.items.find((it) => String(it.id) === itemIdStr)
        if (item) {
          inventoryStore.logMovement(itemIdStr, item.name, m.quantity ?? m.qty ?? 0, 'stock-out', { bookingId, taskId })
          // also decrement local quantity to reflect server action
          item.quantity = Math.max(0, item.quantity - (m.quantity ?? m.qty ?? 0))
        }
      })
    } else {
      // fallback: apply locally
      validLines.forEach((line) => {
        inventoryStore.stockOut(line.itemId, line.quantity, { taskId, bookingId })
      })
    }
    // if bookingId provided, attach images to booking locally as well (server may also do it)
    try {
      if (bookingId !== null) {
        const bookingsStore = useBookingsStore()
        const existing = await bookingsStore.getBooking(bookingId)
        const beforeList = Array.isArray(existing?.beforeImages) ? existing.beforeImages.slice() : []
        const afterList = Array.isArray(existing?.afterImages) ? existing.afterImages.slice() : []
        if (recordForm.beforeImagePreview) beforeList.push(recordForm.beforeImagePreview)
        if (recordForm.afterImagePreview) afterList.push(recordForm.afterImagePreview)
        await bookingsStore.updateBooking(bookingId, { beforeImages: beforeList, afterImages: afterList })
      }
    } catch (e) {
      // ignore booking patch errors
    }
  } catch (err) {
    // network or server error — apply local changes so UI remains usable
    validLines.forEach((line) => {
      inventoryStore.stockOut(line.itemId, line.quantity, { taskId, bookingId })
    })
    // also patch booking locally with previews if bookingId provided
    try {
      if (bookingId !== null) {
        const bookingsStore = useBookingsStore()
        const existing = await bookingsStore.getBooking(bookingId)
        const beforeList = Array.isArray(existing?.beforeImages) ? existing.beforeImages.slice() : []
        const afterList = Array.isArray(existing?.afterImages) ? existing.afterImages.slice() : []
        if (recordForm.beforeImagePreview) beforeList.push(recordForm.beforeImagePreview)
        if (recordForm.afterImagePreview) afterList.push(recordForm.afterImagePreview)
        await bookingsStore.updateBooking(bookingId, { beforeImages: beforeList, afterImages: afterList })
      }
    } catch (e) {
      // ignore
    }
  }

  closeRecordModal()
}

const hasDuplicateAssignees = computed(() => {
  const ids = newTaskForm.value.assignedStaffIds
  return new Set(ids).size !== ids.length
})

function updateRequiredStaffCount(count: number) {
  const next = [...newTaskForm.value.assignedStaffIds]
  if (next.length < count) {
    const fallback = staffList.value[0]?.id || ''
    while (next.length < count) next.push(fallback)
  } else if (next.length > count) {
    next.length = count
  }

  newTaskForm.value.requiredStaffCount = count
  newTaskForm.value.assignedStaffIds = next
}

function formatDate(isoDate: string) {
  if (!isoDate) return '-'
  return new Date(isoDate).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function getStatusClass(status: TaskStatus) {
  if (status === 'done') return 'bg-green-100 text-green-700'
  if (status === 'in-progress') return 'bg-blue-100 text-blue-700'
  return 'bg-gray-100 text-gray-700'
}

function getStaffName(staffId: string) {
  return staffList.value.find((staff) => staff.id === staffId)?.name || `Staff #${staffId}`
}

function getTeamLabel(staffIds: string[]) {
  if (!staffIds?.length) return 'No team assigned'
  return staffIds.map((id) => getStaffName(id)).join(', ')
}

function formatTaskLocation(task: {
  location?: {
    country?: string
    region?: string
    province?: string
    municipality?: string
    barangay?: string
    house?: string
  }
}) {
  const loc = task.location
  if (!loc) return 'No location set'

  const parts = [loc.house, loc.barangay, loc.municipality, loc.province, loc.region, loc.country].filter(Boolean)
  return parts.length ? parts.join(', ') : 'No location set'
}

function assignTask() {
  const { projectName, title, description, assignedStaffIds, requiredStaffCount, dueDate, location } = newTaskForm.value
  if (!projectName || !title || !dueDate) return
  if (!location.province || !location.municipality || !location.barangay || !location.house) return
  if (assignedStaffIds.length !== requiredStaffCount) return
  if (assignedStaffIds.some((id) => !id)) return
  if (new Set(assignedStaffIds).size !== assignedStaffIds.length) return

  staffTasksStore.assignTask({
    projectName,
    title,
    description,
    assignedStaffIds,
    dueDate,
    location: {
      province: location.province,
      municipality: location.municipality,
      barangay: location.barangay,
      house: location.house,
    },
  })

  newTaskForm.value = {
    projectName: '',
    title: '',
    description: '',
    requiredStaffCount: 2,
    assignedStaffIds: ['1', '2'],
    dueDate: '',
    location: {
      country: 'PH',
      region: 'Bicol Region (Region V)',
      province: '',
      municipality: '',
      barangay: '',
      house: '',
    },
  }
}

function updateTaskStatus(taskId: string, status: TaskStatus) {
  // when staff tries to mark done, require recording materials used first
  if (status === 'done' && !isAdmin.value) {
    const movements = inventoryStore.getMovementsForTask(taskId)
    const hasUsedMaterials = movements.some((m) => m.type === 'stock-out')
    if (!hasUsedMaterials) {
      // open record modal to force recording materials before completion
      openRecordModal(taskId)
      return
    }
  }

  staffTasksStore.updateTaskStatus(taskId, status)
}

function removeTask(taskId: string) {
  staffTasksStore.removeTask(taskId)
}
</script>

<template>
  <section class="space-y-6">
    <div>
      <h3 class="mb-1 text-2xl font-semibold text-gray-900">Staff Tasks</h3>
      <p class="text-sm text-gray-600">Assigned project tasks and progress tracking</p>
    </div>

    <div v-if="isAdmin" class="rounded-lg border border-gray-200 bg-white p-6">
      <h4 class="mb-4 text-lg font-semibold text-gray-900">Staff Management: Assign Tasks</h4>

      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <input v-model="newTaskForm.projectName" type="text" placeholder="Project name" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.title" type="text" placeholder="Task title" class="rounded-lg border border-gray-300 px-3 py-2" />

        <select :value="newTaskForm.requiredStaffCount" class="rounded-lg border border-gray-300 px-3 py-2" @change="updateRequiredStaffCount(Number(($event.target as HTMLSelectElement).value))">
          <option v-for="count in staffCountOptions" :key="count" :value="count">{{ count }} Staff Needed</option>
        </select>

        <input v-model="newTaskForm.dueDate" type="date" class="rounded-lg border border-gray-300 px-3 py-2" />

        <div class="md:col-span-2 grid grid-cols-1 gap-3 md:grid-cols-2">
          <select v-for="(_, index) in newTaskForm.assignedStaffIds" :key="`assign-staff-${index}`" v-model="newTaskForm.assignedStaffIds[index]" class="rounded-lg border border-gray-300 px-3 py-2">
            <option v-for="staff in staffList" :key="staff.id" :value="staff.id">Staff {{ index + 1 }}: {{ staff.name }}</option>
          </select>
        </div>

        <input :value="newTaskForm.location.country" type="text" disabled class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600" />
        <input :value="newTaskForm.location.region" type="text" disabled class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600" />
        <input v-model="newTaskForm.location.province" type="text" placeholder="Province" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.location.municipality" type="text" placeholder="Municipality" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.location.barangay" type="text" placeholder="Barangay" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.location.house" type="text" placeholder="House / Street" class="rounded-lg border border-gray-300 px-3 py-2" />

        <p v-if="hasDuplicateAssignees" class="md:col-span-2 text-sm text-red-600">Please select different staff for each slot.</p>
        <p v-if="newTaskForm.requiredStaffCount > staffList.length" class="md:col-span-2 text-sm text-amber-600">You selected {{ newTaskForm.requiredStaffCount }} staff but only {{ staffList.length }} staff are available now.</p>

        <textarea v-model="newTaskForm.description" rows="3" placeholder="Task description" class="md:col-span-2 rounded-lg border border-gray-300 px-3 py-2" />
      </div>

      <div class="mt-3">
        <button type="button" class="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300" :disabled="hasDuplicateAssignees || newTaskForm.requiredStaffCount > staffList.length" @click="assignTask">Assign Task</button>
      </div>

      <div class="mt-6">
        <h5 class="mb-3 font-semibold text-gray-900">All Assigned Tasks</h5>
        <div v-if="staffTasksStore.tasks.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">No assigned tasks yet.</div>
        <div v-else class="space-y-3">
          <div v-for="task in staffTasksStore.tasks" :key="task.id" class="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p class="font-semibold text-gray-900">{{ task.title }}</p>
                <p class="text-sm text-gray-600">{{ task.projectName }} · Team: {{ getTeamLabel(task.assignedStaffIds) }}</p>
              </div>
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="getStatusClass(task.status)">{{ task.status }}</span>
            </div>

            <p class="mt-2 text-sm text-gray-700">{{ task.description || 'No description' }}</p>
            <p class="mt-2 text-xs text-gray-500">Due: {{ formatDate(task.dueDate) }}</p>
            <p class="mt-1 text-xs text-gray-500">Location: {{ formatTaskLocation(task) }}</p>

            <div class="mt-3 flex flex-wrap gap-2">
              <select :value="task.status" class="rounded-lg border border-gray-300 px-2 py-1 text-sm" @change="updateTaskStatus(task.id, ($event.target as HTMLSelectElement).value as TaskStatus)">
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="done">Done</option>
              </select>
                <button type="button" class="rounded-lg bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-700 hover:bg-amber-200" @click="openRecordModal(task.id)">Record Materials</button>
              <button type="button" class="rounded-lg bg-red-100 px-3 py-1 text-sm font-semibold text-red-700 hover:bg-red-200" @click="removeTask(task.id)">Remove</button>
            </div>
          </div>
        </div>
      </div>
    </div>

      <div v-if="isRecordModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="closeRecordModal">
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <h4 class="mb-4 text-lg font-semibold text-gray-900">Record Materials Used</h4>
          <div class="space-y-4">
            <div class="space-y-3">
              <div v-for="(line, index) in recordForm.lines" :key="`material-line-${index}`" class="rounded-lg border border-gray-200 p-3">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-gray-700">Material {{ index + 1 }}</p>
                  <button
                    type="button"
                    class="rounded bg-red-100 px-2 py-1 text-xs font-semibold text-red-700 hover:bg-red-200 disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="recordForm.lines.length === 1"
                    @click="removeMaterialLine(index)"
                  >
                    Remove
                  </button>
                </div>

                <div class="mt-2">
                  <label class="block text-sm font-medium text-gray-700">Item</label>
                  <select v-model="line.itemId" class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3">
                    <option v-for="it in inventoryStore.items" :key="it.id" :value="it.id">{{ it.name }} — {{ it.quantity }} left</option>
                  </select>
                </div>

                <div class="mt-2">
                  <label class="block text-sm font-medium text-gray-700">Quantity Used</label>
                  <input v-model.number="line.quantity" type="number" min="1" class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3" />
                </div>
              </div>

              <button type="button" class="w-full rounded-lg border border-blue-300 bg-blue-50 px-3 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-100" @click="addMaterialLine">
                + Add Another Material
              </button>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Booking ID (optional)</label>
              <input v-model="recordForm.bookingId" type="text" placeholder="Link to booking id (optional)" class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Before Image (required)</label>
              <input type="file" accept="image/*" class="mt-1 w-full text-sm" @change="handleBeforeImageChange" />
              <div v-if="recordForm.beforeImagePreview" class="mt-2">
                <p class="text-xs text-gray-600">Preview:</p>
                <img :src="recordForm.beforeImagePreview" class="max-h-40 mt-1 rounded-lg border" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">After Image (required)</label>
              <input type="file" accept="image/*" class="mt-1 w-full text-sm" @change="handleAfterImageChange" />
              <div v-if="recordForm.afterImagePreview" class="mt-2">
                <p class="text-xs text-gray-600">Preview:</p>
                <img :src="recordForm.afterImagePreview" class="max-h-40 mt-1 rounded-lg border" />
              </div>
            </div>

            <div class="flex gap-3 pt-2">
              <button type="button" class="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50" @click="closeRecordModal">Cancel</button>
              <button type="button" class="flex-1 rounded-lg bg-green-600 px-4 py-2 font-semibold text-white hover:bg-green-700" @click="recordMaterialsUsage">Record</button>
            </div>
          </div>
        </div>
      </div>

    <div v-if="!isAdmin" class="rounded-lg border border-gray-200 bg-white p-6">
      <h4 class="mb-4 text-lg font-semibold text-gray-900">My Assigned Tasks</h4>
      <p class="mb-4 text-sm text-blue-700">Record and submit used materials here. Booking completion is handled by admin in Booking Approval.</p>
      <div v-if="myAssignedTasks.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">No tasks assigned yet.</div>
      <div v-else class="space-y-3">
        <div v-for="task in myAssignedTasks" :key="task.id" class="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p class="font-semibold text-gray-900">{{ task.title }}</p>
              <p class="text-sm text-gray-600">{{ task.projectName }}</p>
              <p class="text-xs text-gray-500">Team: {{ getTeamLabel(task.assignedStaffIds) }}</p>
            </div>
            <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="getStatusClass(task.status)">{{ task.status }}</span>
          </div>

          <p class="mt-2 text-sm text-gray-700">{{ task.description || 'No description' }}</p>
          <p class="mt-2 text-xs text-gray-500">Due: {{ formatDate(task.dueDate) }}</p>
          <p class="mt-1 text-xs text-gray-500">Location: {{ formatTaskLocation(task) }}</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <button type="button" class="rounded-lg bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-700 hover:bg-amber-200" @click="openRecordModal(task.id)">Record & Submit Materials</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
