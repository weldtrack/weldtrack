<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Clipboard } from 'lucide-vue-next'
import { useAuthStore } from '../../../stores/auth'
import { useStaffTasksStore } from '../../../stores/staffTasks'
import { type TaskStatus } from '../../../types/staffTasks'
import { useInventoryStore } from '../../../stores/inventory'
import api from '../../../api/api'
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
const assignedBookingIds = computed(() => {
  return new Set(
    staffTasksStore.tasks
      .map((task) => task.bookingId)
      .filter((bookingId): bookingId is number => bookingId != null),
  )
})
const confirmedBookings = computed(() =>
  Array.isArray(bookingsStore.bookings)
    ? bookingsStore.bookings.filter((booking) => {
        return booking.status === 'confirmed' && !assignedBookingIds.value.has(booking.id)
      })
    : [],
)

const staffCountOptions = [2, 4, 6, 8, 10]

const currentUserId = ref('')
const selectedBookingId = ref<number | null>(null)

const myAssignedTasks = computed(() => {
  return staffTasksStore.tasks.filter((task) => task.assignedStaffIds.includes(currentUserId.value))
})

const getTodayDate = () => new Date().toISOString().split('T')[0]

const newTaskForm = ref({
  projectName: '',
  title: '',
  description: '',
  requiredStaffCount: 2,
  assignedStaffIds: ['' , ''] as string[],
  dueDate: getTodayDate(),
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
const isRemoveTaskModalOpen = ref(false)
const taskToRemove = ref<{ id: string; title: string } | null>(null)

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

function resetRecordForm() {
  recordForm.lines = [{ itemId: inventoryStore.items[0]?.id || '', quantity: 1 }]
  recordForm.bookingId = ''
  recordForm.beforeImageFile = null
  recordForm.afterImageFile = null
  recordForm.beforeImagePreview = ''
  recordForm.afterImagePreview = ''
}

function getTaskBookingId(taskId: string) {
  const task = staffTasksStore.tasks.find((entry) => entry.id === taskId)
  if (task?.bookingId != null) return task.bookingId
  const movement = inventoryStore.getMovementsForTask(taskId).find((entry) => entry.bookingId != null)
  return movement?.bookingId ?? null
}

function hasRecordedMaterialsForTask(taskId: string) {
  return inventoryStore.getMovementsForTask(taskId).some((entry) => entry.type === 'stock-out')
}

function isTaskBookingCompleted(taskId: string) {
  const bookingId = getTaskBookingId(taskId)
  if (bookingId == null) return false
  const booking = bookingsStore.bookings.find((entry) => entry.id === bookingId)
  return booking?.status === 'completed'
}

async function openRecordModal(taskId: string) {
  recordingTask.value = taskId
  resetRecordForm()

  await inventoryStore.fetchMovements()

  const bookingId = getTaskBookingId(taskId)
  if (bookingId != null) {
    recordForm.bookingId = String(bookingId)

    const booking = await bookingsStore.getBooking(bookingId)
    if (booking.status === 'completed') {
      modalStore.open({
        title: 'Booking already completed',
        message: 'Recorded materials can no longer be updated after admin completes the booking.',
        variant: 'warning',
      })
      closeRecordModal()
      return
    }

    if (Array.isArray(booking.materials) && booking.materials.length > 0) {
      recordForm.lines = booking.materials.map((line) => ({
        itemId: String(line.itemId),
        quantity: Number(line.qty) || 1,
      }))
    }

    if (booking.beforeImages?.length) {
      recordForm.beforeImagePreview = String(booking.beforeImages[0] || '')
    }
    if (booking.afterImages?.length) {
      recordForm.afterImagePreview = String(booking.afterImages[0] || '')
    }
  }

  isRecordModalOpen.value = true
}

function selectConfirmedBooking(bookingId: number) {
  const booking = confirmedBookings.value.find((item) => item.id === bookingId)
  if (!booking) return

  selectedBookingId.value = booking.id
  newTaskForm.value.projectName = `${booking.projectType} - ${booking.email || booking.customerName || `Booking #${booking.id}`}`
  newTaskForm.value.title = booking.projectType
  newTaskForm.value.description = booking.description || ''
  newTaskForm.value.dueDate = booking.scheduleDate || booking.preferredDate || getTodayDate()
  // copy booking location if available
  if (booking.location) {
    newTaskForm.value.location.province = booking.location.province || ''
    newTaskForm.value.location.municipality = booking.location.municipality || ''
    newTaskForm.value.location.barangay = booking.location.barangay || ''
    newTaskForm.value.location.house = booking.location.house || ''
  }
}

onMounted(async () => {
  await Promise.all([
    authStore.fetchStaffDirectory(),
    api.get('/auth/me').then(({ data }) => {
      currentUserId.value = String(data?.id ?? '')
    }),
    bookingsStore.fetchBookings({ limit: 100 }),
    staffTasksStore.fetchTasks(),
    inventoryStore.fetchInventory(),
    inventoryStore.fetchMovements(),
  ])
})

function closeRecordModal() {
  isRecordModalOpen.value = false
  recordingTask.value = null
  resetRecordForm()
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

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
    minimumFractionDigits: 2,
  }).format(amount)
}

function getItemPrice(itemId: string) {
  const item = inventoryStore.items.find((entry) => entry.id === itemId)
  return Number(item?.unitPrice ?? 0)
}

function getLineTotal(itemId: string, quantity: number) {
  return getItemPrice(itemId) * Math.max(0, Number(quantity) || 0)
}

const materialsTotalPrice = computed(() => {
  return recordForm.lines.reduce((total, line) => {
    return total + getLineTotal(line.itemId, line.quantity)
  }, 0)
})

async function recordMaterialsUsage() {
  if (!recordingTask.value) return
  const bookingId = getTaskBookingId(recordingTask.value)
  if (!Number.isFinite(Number(bookingId)) || Number(bookingId) <= 0) {
    modalStore.open({
      title: 'Missing booking link',
      message: 'This task is not linked to a booking yet. Reassign it from a confirmed booking first.',
      variant: 'warning',
    })
    return
  }

  const validLines = recordForm.lines.filter((line) => line.itemId && line.quantity > 0)
  if (validLines.length === 0) return

  const taskId = recordingTask.value

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
  await api.post(`/bookings/${Number(bookingId)}/materials`, payload)
  await inventoryStore.fetchInventory()
  await inventoryStore.fetchMovements()

  await staffTasksStore.updateTaskStatus(recordingTask.value, 'done')

  await bookingsStore.getBooking(Number(bookingId))

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
    dueDate: getTodayDate(),
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

function getTeamLabel(task: { assignedStaffIds?: string[]; assignedStaffEmails?: string[] }) {
  if (task.assignedStaffEmails?.length) return task.assignedStaffEmails.join(', ')
  if (!task.assignedStaffIds?.length) return 'No team assigned'

  const labels = task.assignedStaffIds
    .map((id) => authStore.getStaffLabel(id))
    .filter(Boolean)

  return labels.length ? labels.join(', ') : 'Unassigned'
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
  if (!selectedBookingId.value) {
    modalStore.open({
      title: 'Booking required',
      message: 'Please select a confirmed booking to assign a task.',
      variant: 'warning',
    })
    return
  }

  const { projectName, title, description, assignedStaffIds, requiredStaffCount, dueDate, location } = newTaskForm.value
  if (!projectName || !title || !dueDate) return
  if (!location.province || !location.municipality || !location.barangay || !location.house) return
  if (assignedStaffIds.length !== requiredStaffCount) return
  if (assignedStaffIds.some((id) => !id)) return
  if (new Set(assignedStaffIds).size !== assignedStaffIds.length) return

  await staffTasksStore.assignTask({
    bookingId: selectedBookingId.value,
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

function openRemoveTaskModal(task: { id: string; title: string }) {
  taskToRemove.value = { id: task.id, title: task.title }
  isRemoveTaskModalOpen.value = true
}

function closeRemoveTaskModal() {
  isRemoveTaskModalOpen.value = false
  taskToRemove.value = null
}

async function confirmRemoveTask() {
  if (!taskToRemove.value) return
  await staffTasksStore.removeTask(taskToRemove.value.id)
  closeRemoveTaskModal()
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex items-start gap-3">
      <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-slate-50 to-white ring-1 ring-slate-100">
        <Clipboard class="h-6 w-6 text-slate-700" />
      </div>
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">Staff Tasks</h3>
        <p class="text-sm text-gray-600">Assigned project tasks and progress tracking</p>
      </div>
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
        <div class="md:col-span-2">
          <label class="mb-2 block text-sm font-semibold text-gray-700" for="requiredStaffCount">Staff Needed</label>
          <select
            id="requiredStaffCount"
            :value="newTaskForm.requiredStaffCount"
            class="w-full rounded-lg border border-gray-300 px-3 py-2"
            @change="updateRequiredStaffCount(Number(($event.target as HTMLSelectElement).value))"
          >
            <option v-for="count in staffCountOptions" :key="count" :value="count">{{ count }} Staff Needed</option>
          </select>
        </div>

        <div class="md:col-span-2">
          <p class="mb-2 text-sm font-semibold text-gray-700">Assign Staff Members</p>
          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
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
        </div>

        <div class="md:col-span-2 mt-2">
          <p class="text-sm font-semibold text-gray-700">Project Information (Auto-filled from booking)</p>
        </div>

        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">Project Name</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.projectName || '-' }}</p>
        </div>
        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">Task Title</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.title || '-' }}</p>
        </div>

        <input v-model="newTaskForm.dueDate" type="date" class="rounded-lg border border-gray-300 px-3 py-2" />

        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">Country</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.location.country || '-' }}</p>
        </div>
        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">Region</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.location.region || '-' }}</p>
        </div>
        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">Province</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.location.province || '-' }}</p>
        </div>
        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">Municipality</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.location.municipality || '-' }}</p>
        </div>
        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">Barangay</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.location.barangay || '-' }}</p>
        </div>
        <div class="rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-gray-600">
          <p class="text-xs text-gray-500">House / Street</p>
          <p class="text-sm font-medium text-gray-900">{{ newTaskForm.location.house || '-' }}</p>
        </div>

        <p v-if="hasDuplicateAssignees" class="md:col-span-2 text-sm text-red-600">Please select different staff for each slot.</p>

        <div class="md:col-span-2 rounded-lg border border-gray-300 bg-gray-100 px-3 py-2">
          <p class="text-xs text-gray-500">Description</p>
          <p class="text-sm text-gray-900">{{ newTaskForm.description || '-' }}</p>
        </div>
      </div>

      <div class="mt-3">
        <button type="button" class="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300" :disabled="!selectedBookingId || hasDuplicateAssignees" @click="assignTask">Assign Task</button>
        <p v-if="!selectedBookingId" class="mt-2 text-sm text-amber-600">⚠ Select a confirmed booking first to assign a task</p>
      </div>

      <div class="mt-6">
        <h5 class="mb-3 font-semibold text-gray-900">All Assigned Tasks</h5>
        <div v-if="staffTasksStore.tasks.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">No assigned tasks yet.</div>
        <div v-else class="space-y-3">
          <div v-for="task in staffTasksStore.tasks" :key="task.id" class="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p class="font-semibold text-gray-900">{{ task.title }}</p>
                <p class="text-sm text-gray-600">{{ task.projectName }} · Team: {{ getTeamLabel(task) }}</p>
              </div>
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="getStatusClass(task.status)">{{ task.status }}</span>
            </div>

            <p class="mt-2 text-sm text-gray-700">{{ task.description || 'No description' }}</p>
            <p class="mt-2 text-xs text-gray-500">Due: {{ formatDate(task.dueDate) }}</p>
            <p class="mt-1 text-xs text-gray-500">Location: {{ formatTaskLocation(task) }}</p>
            <p v-if="isTaskBookingCompleted(task.id)" class="mt-2 text-xs font-semibold text-green-700">Task completed</p>

            <div class="mt-3 flex flex-wrap gap-2">
              <button v-if="!isTaskBookingCompleted(task.id)" type="button" class="rounded-lg bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-700 hover:bg-amber-200" @click="openRecordModal(task.id)">{{ hasRecordedMaterialsForTask(task.id) ? 'Update Materials' : 'Record Materials' }}</button>
              <button type="button" class="rounded-lg bg-red-100 px-3 py-1 text-sm font-semibold text-red-700 hover:bg-red-200" @click="openRemoveTaskModal(task)">Remove</button>
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
                  <option v-for="it in inventoryStore.items" :key="it.id" :value="it.id">{{ it.name }} — {{ formatCurrency(it.unitPrice) }} — {{ getItemQuantity(it.id) }} left</option>
                </select>
              </div>

              <div class="mt-2">
                <label class="block text-sm font-medium text-gray-700">Quantity Used</label>
                <input v-model.number="line.quantity" type="number" min="1" class="mt-1 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm" />
              </div>

              <div class="mt-3 grid grid-cols-1 gap-2 rounded-xl bg-white px-4 py-3 text-sm text-gray-600 sm:grid-cols-2">
                <p>Unit Price: <span class="font-semibold text-gray-900">{{ formatCurrency(getItemPrice(line.itemId)) }}</span></p>
                <p>Line Total: <span class="font-semibold text-gray-900">{{ formatCurrency(getLineTotal(line.itemId, line.quantity)) }}</span></p>
              </div>
            </div>

            <button type="button" class="w-full rounded-xl border border-blue-200 bg-blue-50 px-3 py-2.5 text-sm font-semibold text-blue-700 hover:bg-blue-100" @click="addMaterialLine">
              + Add Another Material
            </button>
          </div>

          <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
            <p class="text-sm text-emerald-700">Estimated total material cost</p>
            <p class="mt-1 text-2xl font-semibold text-emerald-900">{{ formatCurrency(materialsTotalPrice) }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Linked Booking ID</label>
            <div class="mt-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 shadow-sm">
              {{ recordForm.bookingId || 'No linked booking' }}
            </div>
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
          <button type="button" class="rounded-xl bg-linear-to-r from-green-600 to-emerald-600 px-4 py-3 font-semibold text-white shadow-lg shadow-green-600/20 hover:from-green-700 hover:to-emerald-700" @click="recordMaterialsUsage">{{ hasRecordedMaterialsForTask(recordingTask || '') ? 'Update Record' : 'Record' }}</button>
        </template>
      </ModalShell>

      <ModalShell
        :show="isRemoveTaskModalOpen"
        title="Remove Task"
        subtitle="Confirm task removal"
        tone="red"
        size="md"
        @close="closeRemoveTaskModal"
      >
        <div class="space-y-4">
          <p class="text-sm text-gray-700">
            Remove <span class="font-semibold text-gray-900">{{ taskToRemove?.title || 'this task' }}</span>?
          </p>
          <p class="text-sm text-red-700">
            This action cannot be undone.
          </p>
        </div>

        <template #footer>
          <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeRemoveTaskModal">Cancel</button>
          <button type="button" class="rounded-xl bg-linear-to-r from-red-600 to-rose-600 px-4 py-3 font-semibold text-white shadow-lg shadow-red-600/20 hover:from-red-700 hover:to-rose-700" @click="confirmRemoveTask">Remove Task</button>
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
              <p class="text-xs text-gray-500">Team: {{ getTeamLabel(task) }}</p>
            </div>
            <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="getStatusClass(task.status)">{{ task.status }}</span>
          </div>

          <p class="mt-2 text-sm text-gray-700">{{ task.description || 'No description' }}</p>
          <p class="mt-2 text-xs text-gray-500">Due: {{ formatDate(task.dueDate) }}</p>
          <p class="mt-1 text-xs text-gray-500">Location: {{ formatTaskLocation(task) }}</p>
          <p v-if="isTaskBookingCompleted(task.id)" class="mt-2 text-xs font-semibold text-green-700">Task completed</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <button v-if="!isTaskBookingCompleted(task.id)" type="button" class="rounded-lg bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-700 hover:bg-amber-200" @click="openRecordModal(task.id)">{{ hasRecordedMaterialsForTask(task.id) ? 'Update Submitted Materials' : 'Record & Submit Materials' }}</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
