<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '../../../stores/auth'
import { useStaffTasksStore, type TaskStatus } from '../../../stores/staffTasks'
import { useInventoryStore } from '../../../stores/inventory'
import api from '../../../services/api'
import { useBookingsStore } from '../../../stores/bookings'
import { useModalStore } from '../../../stores/modal'
import ModalShell from '../../../components/ui/ModalShell.vue'

interface StaffMember {
  id: string
  email: string
}

const authStore = useAuthStore()
const staffTasksStore = useStaffTasksStore()
const bookingsStore = useBookingsStore()
const modalStore = useModalStore()
const isAdmin = computed(() => authStore.role === 'admin')

const staffList = computed(() => authStore.staffDirectory as StaffMember[])
const confirmedBookings = computed(() =>
  Array.isArray(bookingsStore.bookings)
    ? bookingsStore.bookings.filter((booking) => booking.status === 'confirmed')
    : [],
)

const staffCountOptions = [2, 4, 6, 8, 10]

const currentUserId = ref('')
const selectedBookingId = ref<number | null>(null)

const myAssignedTasks = computed(() => {
  return staffTasksStore.tasks.filter((task) => task.assignedStaffIds.includes(currentUserId.value))
})

const newTaskForm = ref({
  projectName: '',
  title: '',
  description: '',
  requiredStaffCount: 2,
  assignedStaffIds: ['' , ''] as string[],
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
  // initialize with first available item if present
  recordForm.lines = [{ itemId: inventoryStore.items[0]?.id || '', quantity: 1 }]
  recordForm.bookingId = ''
  recordForm.beforeImageFile = null
  recordForm.afterImageFile = null
  recordForm.beforeImagePreview = ''
  recordForm.afterImagePreview = ''
  // debug: inspect inventory at modal open
  // eslint-disable-next-line no-console
  console.debug('Opening Record Modal — inventory items:', inventoryStore.items)
  isRecordModalOpen.value = true
}

function selectConfirmedBooking(bookingId: number) {
  const booking = confirmedBookings.value.find((item) => item.id === bookingId)
  if (!booking) return

  selectedBookingId.value = booking.id
  const today = new Date().toISOString().split('T')[0]
  newTaskForm.value.projectName = `${booking.projectType} - ${booking.email || booking.customerName || `Booking #${booking.id}`}`
  newTaskForm.value.title = booking.projectType
  newTaskForm.value.description = booking.description || ''
  newTaskForm.value.dueDate = booking.scheduleDate || booking.preferredDate || today
}

onMounted(async () => {
  await Promise.all([
    authStore.fetchStaffDirectory(),
    api.get('/auth/me').then(({ data }) => {
      currentUserId.value = String(data?.id ?? '')
    }),
    bookingsStore.fetchBookings(),
    staffTasksStore.fetchTasks(),
    inventoryStore.fetchInventory(),
    inventoryStore.fetchMovements(),
  ])
})

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
  const bookingIdRaw = (recordForm.bookingId || '').toString().trim()
  if (!bookingIdRaw) {
    modalStore.open({
      title: 'Booking ID required',
      message: 'Please enter a booking ID before submitting materials.',
      variant: 'warning',
    })
    return
  }
  const bookingId = Number(bookingIdRaw)
  if (!Number.isFinite(bookingId) || bookingId <= 0) {
    modalStore.open({
      title: 'Invalid booking ID',
      message: 'Booking ID must be a valid number.',
      variant: 'warning',
    })
    return
  }

  const validLines = recordForm.lines.filter((line) => line.itemId && line.quantity > 0)
  if (validLines.length === 0) return

  const taskId = recordingTask.value

  // Require both before and after images to be attached
  if (!recordForm.beforeImagePreview || !recordForm.afterImagePreview) {
    modalStore.open({
      title: 'Images required',
      message: 'Please attach both before and after images before submitting.',
      variant: 'warning',
    })
    return
  }

  const payload = {
    submittedBy: Number(currentUserId.value) || undefined,
    taskId,
    movementType: 'stock_out',
    lines: validLines.map((l) => ({ itemId: Number(l.itemId), quantity: l.quantity })),
    beforeImage: recordForm.beforeImagePreview || undefined,
    afterImage: recordForm.afterImagePreview || undefined,
  }
  await api.post(`/bookings/${bookingId}/materials`, payload)
  await inventoryStore.fetchInventory()
  await inventoryStore.fetchMovements()

  // Auto-mark task as done after successful submission
  await staffTasksStore.updateTaskStatus(recordingTask.value, 'done')

  const bookingsStore = useBookingsStore()
  await bookingsStore.getBooking(bookingId)

  closeRecordModal()
}

const hasDuplicateAssignees = computed(() => {
  const ids = newTaskForm.value.assignedStaffIds
  return new Set(ids).size !== ids.length
})

const selectedBookingLabel = computed(() => {
  if (selectedBookingId.value == null) return 'No booking selected'
  const booking = confirmedBookings.value.find((item) => item.id === selectedBookingId.value)
  if (!booking) return 'No booking selected'
  return `${booking.projectType} · ${booking.email || booking.customerName || `Booking #${booking.id}`}`
})

function updateRequiredStaffCount(count: number) {
  const next = [...newTaskForm.value.assignedStaffIds]
  if (next.length < count) {
    const fallback = ''
    while (next.length < count) next.push(fallback)
  } else if (next.length > count) {
    next.length = count
  }

  newTaskForm.value.requiredStaffCount = count
  newTaskForm.value.assignedStaffIds = next
}

function resetNewTaskForm() {
  selectedBookingId.value = null
  newTaskForm.value = {
    projectName: '',
    title: '',
    description: '',
    requiredStaffCount: 2,
    assignedStaffIds: ['', ''],
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
  return authStore.getStaffLabel(staffId, staffId ? `Staff #${staffId}` : 'Unassigned')
}

function getTeamLabel(staffIds: string[]) {
  if (!staffIds?.length) return 'No team assigned'
  return staffIds.map((id) => getStaffName(id)).join(', ')
}

function getItemQuantity(itemId: string) {
  const it = inventoryStore.items.find((i) => i.id === itemId)
  return it ? it.quantity : 0
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

async function assignTask() {
  const { projectName, title, description, assignedStaffIds, requiredStaffCount, dueDate, location } = newTaskForm.value
  if (!projectName || !title || !dueDate) return
  if (!location.province || !location.municipality || !location.barangay || !location.house) return
  if (assignedStaffIds.length !== requiredStaffCount) return
  if (assignedStaffIds.some((id) => !id)) return
  if (new Set(assignedStaffIds).size !== assignedStaffIds.length) return

  await staffTasksStore.assignTask({
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

    resetNewTaskForm()
}

async function updateTaskStatus(taskId: string, status: TaskStatus) {
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

  await staffTasksStore.updateTaskStatus(taskId, status)
}

async function removeTask(taskId: string) {
  await staffTasksStore.removeTask(taskId)
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

      <div class="mb-5 rounded-xl border border-blue-200 bg-blue-50 p-4">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="text-sm font-semibold text-blue-900">Confirmed Bookings</p>
            <p class="text-xs text-blue-700">Click a confirmed booking to auto-fill the task details.</p>
          </div>
          <p class="text-xs font-medium text-blue-700">Selected: {{ selectedBookingLabel }}</p>
        </div>

        <div v-if="confirmedBookings.length === 0" class="mt-3 rounded-lg bg-white px-3 py-2 text-sm text-gray-500">
          No confirmed bookings yet.
        </div>

        <div v-else class="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
          <button
            v-for="booking in confirmedBookings"
            :key="booking.id"
            type="button"
            class="rounded-xl border px-4 py-3 text-left transition-colors"
            :class="selectedBookingId === booking.id ? 'border-blue-500 bg-blue-100' : 'border-blue-200 bg-white hover:bg-blue-50'"
            @click="selectConfirmedBooking(booking.id)"
          >
            <p class="text-sm font-semibold text-gray-900">{{ booking.projectType }}</p>
            <p class="text-xs text-gray-600">{{ booking.email || booking.customerName || `Booking #${booking.id}` }}</p>
            <p class="mt-1 text-xs text-gray-500">{{ booking.phone || 'No contact number' }}</p>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <input v-model="newTaskForm.projectName" type="text" placeholder="Project name" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.title" type="text" placeholder="Task title" class="rounded-lg border border-gray-300 px-3 py-2" />

        <select :value="newTaskForm.requiredStaffCount" class="rounded-lg border border-gray-300 px-3 py-2" @change="updateRequiredStaffCount(Number(($event.target as HTMLSelectElement).value))">
          <option v-for="count in staffCountOptions" :key="count" :value="count">{{ count }} Staff Needed</option>
        </select>

        <input v-model="newTaskForm.dueDate" type="date" class="rounded-lg border border-gray-300 px-3 py-2" />

        <div class="md:col-span-2 grid grid-cols-1 gap-3 md:grid-cols-2">
          <select
            v-for="(_, index) in newTaskForm.assignedStaffIds"
            :key="`assign-staff-${index}`"
            v-model="newTaskForm.assignedStaffIds[index]"
            class="rounded-lg border border-gray-300 px-3 py-2"
          >
            <option value="">Select staff member</option>
            <option v-for="staff in staffList" :key="staff.id" :value="staff.id">
              {{ staff.email }}
            </option>
          </select>
        </div>

        <input :value="newTaskForm.location.country" type="text" disabled class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600" />
        <input :value="newTaskForm.location.region" type="text" disabled class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600" />
        <input v-model="newTaskForm.location.province" type="text" placeholder="Province" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.location.municipality" type="text" placeholder="Municipality" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.location.barangay" type="text" placeholder="Barangay" class="rounded-lg border border-gray-300 px-3 py-2" />
        <input v-model="newTaskForm.location.house" type="text" placeholder="House / Street" class="rounded-lg border border-gray-300 px-3 py-2" />

        <p v-if="hasDuplicateAssignees" class="md:col-span-2 text-sm text-red-600">Please select different staff for each slot.</p>

        <textarea v-model="newTaskForm.description" rows="3" placeholder="Task description" class="md:col-span-2 rounded-lg border border-gray-300 px-3 py-2" />
      </div>

      <div class="mt-3">
        <button type="button" class="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300" :disabled="hasDuplicateAssignees" @click="assignTask">Assign Task</button>
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

      <ModalShell
        :show="isRecordModalOpen"
        title="Record Materials Used"
        subtitle="Staff submission"
        tone="green"
        size="lg"
        @close="closeRecordModal"
      >
        <div class="space-y-4">
          <div class="space-y-3">
            <div v-for="(line, index) in recordForm.lines" :key="`material-line-${index}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div class="flex items-center justify-between">
                <p class="text-sm font-medium text-slate-700">Material {{ index + 1 }}</p>
                <button
                  type="button"
                  class="rounded-lg bg-red-100 px-2 py-1 text-xs font-semibold text-red-700 hover:bg-red-200 disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="recordForm.lines.length === 1"
                  @click="removeMaterialLine(index)"
                >
                  Remove
                </button>
              </div>

              <div class="mt-2">
                <label class="block text-sm font-medium text-gray-700">Item</label>
                <select v-model="line.itemId" class="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
                  <option v-for="it in inventoryStore.items" :key="it.id" :value="it.id">{{ it.name }} — {{ getItemQuantity(it.id) }} left</option>
                </select>
              </div>

              <div class="mt-2">
                <label class="block text-sm font-medium text-gray-700">Quantity Used</label>
                <input v-model.number="line.quantity" type="number" min="1" class="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm" />
              </div>
            </div>

            <button type="button" class="w-full rounded-xl border border-blue-200 bg-blue-50 px-3 py-2.5 text-sm font-semibold text-blue-700 hover:bg-blue-100" @click="addMaterialLine">
              + Add Another Material
            </button>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Booking ID (required)</label>
            <input v-model="recordForm.bookingId" type="text" placeholder="Link to booking ID" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Before Image (required)</label>
            <input type="file" accept="image/*" class="mt-1 w-full text-sm" @change="handleBeforeImageChange" />
            <div v-if="recordForm.beforeImagePreview" class="mt-2">
              <p class="text-xs text-gray-600">Preview:</p>
              <img :src="recordForm.beforeImagePreview" class="mt-1 max-h-40 rounded-xl border border-slate-200" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">After Image (required)</label>
            <input type="file" accept="image/*" class="mt-1 w-full text-sm" @change="handleAfterImageChange" />
            <div v-if="recordForm.afterImagePreview" class="mt-2">
              <p class="text-xs text-gray-600">Preview:</p>
              <img :src="recordForm.afterImagePreview" class="mt-1 max-h-40 rounded-xl border border-slate-200" />
            </div>
          </div>
        </div>

        <template #footer>
          <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeRecordModal">Cancel</button>
          <button type="button" class="rounded-xl bg-linear-to-r from-green-600 to-emerald-600 px-4 py-3 font-semibold text-white shadow-lg shadow-green-600/20 hover:from-green-700 hover:to-emerald-700" @click="recordMaterialsUsage">Record</button>
        </template>
      </ModalShell>

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
