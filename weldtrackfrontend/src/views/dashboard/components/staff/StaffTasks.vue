<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { Clipboard } from 'lucide-vue-next'
import { useAuthStore } from '../../../../stores/auth'
import { useStaffTasksStore } from '../../../../stores/staffTasks'
import { type TaskStatus } from '../../../../types/staffTasks'
import { useInventoryStore } from '../../../../stores/inventory'
import api from '../../../../api/api'
import { useBookingsStore } from '../../../../stores/bookings'
import { useModalStore } from '../../../../stores/modal'
import { loadServicePriceMap } from '../../../../services/servicePricing'

interface StaffMember {
  id: string
  email: string
}

const authStore = useAuthStore()
const staffTasksStore = useStaffTasksStore()
const bookingsStore = useBookingsStore()
const modalStore = useModalStore()
const servicePriceMap = ref<Record<string, number>>({})
const isLoading = ref(true)
const isAdmin = computed(() => authStore.role === 'admin')

const staffList = computed(() => authStore.staffDirectory as StaffMember[])
const assignedBookingIds = computed(() => {
  return new Set(
    staffTasksStore.tasks
      .map((task) => task.bookingId)
      .filter((bookingId): bookingId is string => bookingId != null),
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
const selectedBookingId = ref<string | null>(null)

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
  laborHours: 0,
})

function resetRecordForm() {
  recordForm.lines = [{ itemId: inventoryStore.items[0]?.id || '', quantity: 1 }]
  recordForm.bookingId = ''
  recordForm.beforeImageFile = null
  recordForm.afterImageFile = null
  recordForm.beforeImagePreview = ''
  recordForm.afterImagePreview = ''
  recordForm.laborHours = 0
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

function selectConfirmedBooking(bookingId: string) {
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
  isLoading.value = true
  try {
    currentUserId.value = String(authStore.user?.id ?? '')

    const requests: Promise<unknown>[] = [
      bookingsStore.fetchBookings({ limit: 100 }),
      staffTasksStore.fetchTasks(),
      inventoryStore.fetchInventory(),
      inventoryStore.fetchMovements(),
      loadServicePriceMap().then((map) => (servicePriceMap.value = map)),
    ]

    // Staff assignment controls are admin-only, so only an admin needs the
    // complete staff directory on this shared screen.
    if (isAdmin.value) requests.push(authStore.fetchStaffDirectory())

    await Promise.all(requests)
  } finally {
    isLoading.value = false
  }
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

function getAssignedStaffCount(taskId: string) {
  const task = staffTasksStore.tasks.find((t) => t.id === taskId)
  return task?.assignedStaffIds?.length || 0
}

function getLaborRate(taskId: string) {
  const task = staffTasksStore.tasks.find((t) => t.id === taskId)
  if (!task) return 0
  const normalizedName = task.projectName.split(' - ')[0].trim().toLowerCase()
  return servicePriceMap.value[normalizedName] || 0
}

function calculateTotalLaborCost(taskId: string) {
  const staffCount = getAssignedStaffCount(taskId)
  const rate = getLaborRate(taskId)
  return recordForm.laborHours * staffCount * rate
}

async function recordMaterialsUsage() {
  if (!recordingTask.value) return
  const bookingId = getTaskBookingId(recordingTask.value)
  if (!bookingId) {
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
    submittedBy: currentUserId.value || undefined,
    taskId,
    movementType: 'stock_out',
    lines: validLines.map((l) => ({ itemId: l.itemId, quantity: l.quantity })),
    laborHours: recordForm.laborHours,
    beforeImage: recordForm.beforeImagePreview || undefined,
    afterImage: recordForm.afterImagePreview || undefined,
  }
  await api.post(`/bookings/${bookingId}/materials`, payload)
  await inventoryStore.fetchInventory()
  await inventoryStore.fetchMovements()

  await staffTasksStore.updateTaskStatus(recordingTask.value, 'done')

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
  if (status === 'in-progress') return 'bg-sky-100 text-sky-700'
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
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />

    <template v-if="!isRecordModalOpen && !isRemoveTaskModalOpen">
      <!-- Header -->
      <div class="flex items-start gap-3">
        <div class="flex h-12 w-12 items-center justify-center">
          <Clipboard class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
        </div>
        <div>
          <h3 class="text-2xl font-semibold text-slate-900">Staff Tasks</h3>
          <p class="text-sm text-slate-600">Assigned project tasks and work progress tracking</p>
        </div>
      </div>

      <!-- Admin Assign Task Form -->
      <div v-if="isAdmin" class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 mt-6">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">Task Assignment</h3>
            <p class="text-sm text-slate-500 mt-1">Assign confirmed customer bookings to staff teams</p>
          </div>
        </div>

        <div class="p-6 space-y-6">
          <!-- Confirmed Bookings Selector -->
          <div class="rounded-xl border border-sky-200 bg-sky-50 p-5 space-y-3">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="text-sm font-bold text-sky-950 dark:text-sky-300">Confirmed Bookings</p>
                <p class="text-xs text-sky-800 dark:text-sky-300">Select a confirmed booking to auto-fill project and location details.</p>
              </div>
              <span class="text-xs font-semibold text-sky-800 dark:text-sky-300 bg-sky-100/80 px-3 py-1 rounded-full border border-sky-200">
                Selected: {{ selectedBookingLabel }}
              </span>
            </div>

            <div v-if="confirmedBookings.length === 0" class="rounded-xl border border-slate-200 bg-white p-4 text-center text-sm text-slate-500">
              No confirmed bookings waiting for assignment.
            </div>

            <div v-else class="grid grid-cols-1 gap-3 md:grid-cols-2">
              <button
                v-for="booking in confirmedBookings"
                :key="booking.id"
                type="button"
                class="rounded-xl border p-4 text-left transition-all duration-200"
                :class="selectedBookingId === booking.id ? 'border-sky-500 bg-white shadow-md ring-2 ring-sky-500/20' : 'border-sky-200 bg-white hover:border-sky-300 hover:shadow-xs'"
                @click="selectConfirmedBooking(booking.id)"
              >
                <p class="text-sm font-bold text-slate-900">{{ booking.projectType }}</p>
                <p class="text-xs text-slate-600 mt-0.5">{{ booking.email || booking.customerName || `Booking #${booking.id}` }}</p>
                <p class="mt-1.5 text-[11px] font-medium text-slate-500">{{ booking.phone || 'No contact number' }}</p>
              </button>
            </div>
          </div>

          <!-- Assignment Configuration Form -->
          <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div class="md:col-span-2">
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="requiredStaffCount">
                Staff Needed <InfoTooltip text="Specify how many staff members are required for this project." />
              </label>
              <select
                id="requiredStaffCount"
                :value="newTaskForm.requiredStaffCount"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
                @change="updateRequiredStaffCount(Number(($event.target as HTMLSelectElement).value))"
              >
                <option v-for="count in staffCountOptions" :key="count" :value="count">{{ count }} Staff Members Required</option>
              </select>
            </div>

            <div class="md:col-span-2">
              <p class="text-sm font-semibold text-gray-700 mb-2">Assign Team Members</p>
              <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <select
                  v-for="(_, index) in newTaskForm.assignedStaffIds"
                  :key="`assign-staff-${index}`"
                  v-model="newTaskForm.assignedStaffIds[index]"
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200 text-sm"
                >
                  <option value="">Select staff member {{ index + 1 }}</option>
                  <option v-for="staff in staffList" :key="staff.id" :value="staff.id">
                    {{ staff.email }}
                  </option>
                </select>
              </div>
            </div>

            <div class="md:col-span-2 pt-2 border-t border-slate-100">
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Project Information (Auto-filled)</p>
            </div>

            <div class="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
              <p class="text-xs text-slate-500 font-medium">Project Name</p>
              <p class="text-sm font-bold text-slate-900 mt-0.5">{{ newTaskForm.projectName || '-' }}</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
              <p class="text-xs text-slate-500 font-medium">Task Title</p>
              <p class="text-sm font-bold text-slate-900 mt-0.5">{{ newTaskForm.title || '-' }}</p>
            </div>

            <div class="md:col-span-2">
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="due-date">Due Date</label>
              <input id="due-date" v-model="newTaskForm.dueDate" type="date" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200" />
            </div>

            <div class="grid grid-cols-2 gap-3 md:col-span-2">
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p class="text-[11px] text-slate-500 font-medium">Province</p>
                <p class="text-sm font-medium text-slate-900">{{ newTaskForm.location.province || '-' }}</p>
              </div>
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p class="text-[11px] text-slate-500 font-medium">Municipality</p>
                <p class="text-sm font-medium text-slate-900">{{ newTaskForm.location.municipality || '-' }}</p>
              </div>
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p class="text-[11px] text-slate-500 font-medium">Barangay</p>
                <p class="text-sm font-medium text-slate-900">{{ newTaskForm.location.barangay || '-' }}</p>
              </div>
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p class="text-[11px] text-slate-500 font-medium">House / Street</p>
                <p class="text-sm font-medium text-slate-900">{{ newTaskForm.location.house || '-' }}</p>
              </div>
            </div>

            <p v-if="hasDuplicateAssignees" class="md:col-span-2 text-xs font-semibold text-red-600 bg-red-50 p-3 rounded-xl border border-red-200">
              Please select different staff members for each team slot.
            </p>

            <div class="md:col-span-2 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-xs text-slate-500 font-medium">Description</p>
              <p class="text-sm text-slate-800 mt-1 leading-relaxed">{{ newTaskForm.description || '-' }}</p>
            </div>
          </div>

          <div class="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p v-if="!selectedBookingId" class="text-xs font-medium text-amber-700">⚠ Select a confirmed booking first to assign a task</p>
            <span v-else class="text-xs font-semibold text-emerald-700">Ready to assign task</span>

            <button
              type="button"
              class="inline-flex min-w-40 items-center justify-center gap-2 rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-6 py-2.5 font-semibold text-white shadow-md shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              :disabled="!selectedBookingId || hasDuplicateAssignees"
              @click="assignTask"
            >
              Assign Task
            </button>
          </div>
        </div>

        <!-- All Assigned Tasks List (Admin View) -->
        <div class="border-t border-slate-200 p-6 space-y-4 bg-slate-50">
          <div class="flex items-center justify-between">
            <h4 class="text-lg font-bold text-slate-900">All Assigned Tasks</h4>
            <span class="text-xs font-bold text-slate-500 bg-slate-200/80 px-2.5 py-1 rounded-full">
              {{ staffTasksStore.tasks.length }} Tasks
            </span>
          </div>

          <div v-if="staffTasksStore.tasks.length === 0" class="rounded-xl border border-slate-200 bg-white p-6 text-center text-sm text-slate-500">
            No tasks assigned yet.
          </div>

          <div v-else class="grid grid-cols-1 gap-4">
            <div
              v-for="task in staffTasksStore.tasks"
              :key="task.id"
              class="rounded-xl border border-slate-200 bg-white p-5 shadow-xs transition-all hover:border-slate-300"
            >
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h5 class="text-base font-bold text-slate-900">{{ task.title }}</h5>
                  <p class="text-xs font-medium text-slate-500 mt-0.5">{{ task.projectName }} · <span class="font-semibold text-slate-700">Team: {{ getTeamLabel(task) }}</span></p>
                </div>
                <span class="rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider" :class="getStatusClass(task.status)">
                  {{ task.status }}
                </span>
              </div>

              <p class="mt-3 text-sm text-slate-700 leading-relaxed">{{ task.description || 'No description provided' }}</p>
              
              <div class="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500 border-t border-slate-100 pt-3">
                <span><strong>Due:</strong> {{ formatDate(task.dueDate) }}</span>
                <span><strong>Location:</strong> {{ formatTaskLocation(task) }}</span>
              </div>

              <p v-if="isTaskBookingCompleted(task.id)" class="mt-2 text-xs font-bold text-emerald-700">✓ Task & Booking Completed</p>

              <div class="mt-4 flex flex-wrap gap-2 justify-end">
                <button
                  v-if="!isTaskBookingCompleted(task.id)"
                  type="button"
                  class="rounded-lg bg-sky-50 border border-sky-200 px-3 py-1.5 text-xs font-semibold text-sky-700 hover:bg-sky-100 transition-colors"
                  @click="openRecordModal(task.id)"
                >
                  {{ hasRecordedMaterialsForTask(task.id) ? 'Update Materials' : 'Record Materials' }}
                </button>
                <button
                  type="button"
                  class="rounded-lg bg-red-50 border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-100 transition-colors"
                  @click="openRemoveTaskModal(task)"
                >
                  Remove Task
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Staff My Tasks View -->
      <div v-if="!isAdmin" class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 mt-6">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">My Assigned Tasks</h3>
            <p class="text-sm text-slate-500 mt-1">Record used materials and submit task progress</p>
          </div>
        </div>

        <div class="p-6">
          <div v-if="myAssignedTasks.length === 0" class="rounded-xl border border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500">
            You have no tasks assigned at the moment.
          </div>

          <div v-else class="grid grid-cols-1 gap-4">
            <div
              v-for="task in myAssignedTasks"
              :key="task.id"
              class="rounded-xl border border-slate-200 bg-white p-5 shadow-xs transition-all hover:border-slate-300"
            >
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h5 class="text-base font-bold text-slate-900">{{ task.title }}</h5>
                  <p class="text-xs font-medium text-slate-500 mt-0.5">{{ task.projectName }}</p>
                  <p class="text-xs font-semibold text-slate-700 mt-1">Team: {{ getTeamLabel(task) }}</p>
                </div>
                <span class="rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider" :class="getStatusClass(task.status)">
                  {{ task.status }}
                </span>
              </div>

              <p class="mt-3 text-sm text-slate-700 leading-relaxed">{{ task.description || 'No description' }}</p>

              <div class="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500 border-t border-slate-100 pt-3">
                <span><strong>Due Date:</strong> {{ formatDate(task.dueDate) }}</span>
                <span><strong>Location:</strong> {{ formatTaskLocation(task) }}</span>
              </div>

              <p v-if="isTaskBookingCompleted(task.id)" class="mt-2 text-xs font-bold text-emerald-700">✓ Task & Booking Completed</p>

              <div class="mt-4 flex flex-wrap gap-2 justify-end">
                <button
                  v-if="!isTaskBookingCompleted(task.id)"
                  type="button"
                  class="rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:from-sky-700 hover:to-sky-800 transition-all"
                  @click="openRecordModal(task.id)"
                >
                  {{ hasRecordedMaterialsForTask(task.id) ? 'Update Submitted Materials' : 'Record & Submit Materials' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="isRecordModalOpen">
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900  max-w-3xl mx-auto">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">Record Materials Used</h3>
            <p class="text-sm text-slate-500 mt-1">Staff submission</p>
          </div>
          <button 
            @click="closeRecordModal" 
            class="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Cancel
          </button>
        </div>

        <div class="p-6">
          <div class="space-y-6">
            <div class="space-y-4">
              <div v-for="(line, index) in recordForm.lines" :key="`material-line-${index}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div class="flex items-center justify-between mb-4">
                  <p class="text-sm font-bold text-slate-800">Material {{ index + 1 }}</p>
                  <button
                    type="button"
                    class="rounded-lg bg-red-50 border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                    :disabled="recordForm.lines.length === 1"
                    @click="removeMaterialLine(index)"
                  >
                    Remove
                  </button>
                </div>

                <div class="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Item<InfoTooltip text="Please provide the item." /></label>
                    <select v-model="line.itemId" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-200 transition">
                      <option v-for="it in inventoryStore.items" :key="it.id" :value="it.id">{{ it.name }} — {{ formatCurrency(it.unitPrice) }} — {{ getItemQuantity(it.id) }} left</option>
                    </select>
                  </div>

                  <div>
                    <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Quantity Used<InfoTooltip text="Please provide the quantity used." /></label>
                    <input v-model.number="line.quantity" type="number" min="1" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-200 transition" />
                  </div>
                </div>

                <div class="mt-4 grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-white px-5 py-4 text-sm text-gray-600 sm:grid-cols-2">
                  <p>Unit Price: <span class="font-bold text-gray-900">{{ formatCurrency(getItemPrice(line.itemId)) }}</span></p>
                  <p>Line Total: <span class="font-bold text-gray-900">{{ formatCurrency(getLineTotal(line.itemId, line.quantity)) }}</span></p>
                </div>
              </div>

              <button type="button" class="w-full rounded-xl border border-dashed border-sky-300 bg-transparent px-4 py-3 text-sm font-semibold text-sky-700 hover:bg-sky-50 hover:border-sky-400 transition-colors" @click="addMaterialLine">
                + Add Another Material
              </button>
            </div>

            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-6 py-5">
              <p class="text-sm font-medium text-emerald-800">Estimated total material cost</p>
              <p class="mt-1 text-3xl font-bold text-emerald-900">{{ formatCurrency(materialsTotalPrice) }}</p>
            </div>

            <div class="space-y-4 rounded-2xl border border-sky-200 bg-sky-50 px-6 py-5">
              <div>
                <label class="flex items-center text-sm font-bold text-sky-900 dark:text-sky-300 mb-1.5">Labor Hours (per member)<InfoTooltip text="Please provide the labor hours per member." /></label>
                <input v-model.number="recordForm.laborHours" type="number" min="0" step="0.5" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-200 transition" />
              </div>
              <p class="text-xs font-medium text-sky-700 dark:text-sky-300">Calculation: {{ recordForm.laborHours }} hours * {{ getAssignedStaffCount(recordingTask || '') }} members * PHP {{ getLaborRate(recordingTask || '') }}/hr</p>
              <p class="text-xl font-bold text-sky-900 dark:text-sky-300">Total Labor Cost: {{ formatCurrency(calculateTotalLaborCost(recordingTask || '')) }}</p>
            </div>

            <div class="grid gap-6 sm:grid-cols-2">
              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Before Image <span class="text-red-500">*</span><InfoTooltip text="Please provide the before image." /></label>
                <input type="file" accept="image/*" class="w-full text-sm file:mr-4 file:rounded-full file:border-0 file:bg-sky-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-sky-700 hover:file:bg-sky-100" @change="handleBeforeImageChange" />
                <div v-if="recordForm.beforeImagePreview" class="mt-3">
                  <img :src="recordForm.beforeImagePreview" class="max-h-48 w-full object-cover rounded-xl border border-slate-200 shadow-sm" />
                </div>
              </div>

              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">After Image <span class="text-red-500">*</span><InfoTooltip text="Please provide the after image." /></label>
                <input type="file" accept="image/*" class="w-full text-sm file:mr-4 file:rounded-full file:border-0 file:bg-sky-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-sky-700 hover:file:bg-sky-100" @change="handleAfterImageChange" />
                <div v-if="recordForm.afterImagePreview" class="mt-3">
                  <img :src="recordForm.afterImagePreview" class="max-h-48 w-full object-cover rounded-xl border border-slate-200 shadow-sm" />
                </div>
              </div>
            </div>
            
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5">Linked Booking ID<InfoTooltip text="Please provide the linked booking id." /></label>
              <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 shadow-sm">
                {{ recordForm.bookingId || 'No linked booking' }}
              </div>
            </div>
          </div>

          <div class="mt-8 pt-6 border-t border-slate-100 flex justify-end gap-3">
            <button type="button" class="rounded-xl border border-slate-200 bg-white px-6 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors" @click="closeRecordModal">Cancel</button>
            <button type="button" class="rounded-xl bg-linear-to-r from-emerald-600 to-green-600 px-8 py-2.5 font-semibold text-white shadow-md shadow-emerald-600/20 hover:from-emerald-700 hover:to-green-700 transition-all" @click="recordMaterialsUsage">{{ hasRecordedMaterialsForTask(recordingTask || '') ? 'Update Record' : 'Record Materials' }}</button>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="isRemoveTaskModalOpen">
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900  max-w-lg mx-auto">
        <div class="border-b border-slate-100 px-6 py-5 bg-transparent">
          <h3 class="text-xl font-bold text-rose-900">Remove Task</h3>
          <p class="text-sm text-rose-600 mt-1">Confirm task removal</p>
        </div>
        
        <div class="p-6">
          <div class="space-y-4">
            <p class="text-slate-700 text-lg">
              Are you sure you want to remove <span class="font-bold text-slate-900">"{{ taskToRemove?.title || 'this task' }}"</span>?
            </p>
            <div class="rounded-xl border border-rose-200 bg-rose-50 p-4">
              <p class="text-sm font-medium text-rose-800 flex items-center gap-2">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                This action cannot be undone.
              </p>
            </div>
          </div>
          
          <div class="mt-8 pt-6 border-t border-slate-100 flex justify-end gap-3">
            <button type="button" class="rounded-xl border border-slate-200 bg-white px-6 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors" @click="closeRemoveTaskModal">Cancel</button>
            <button type="button" class="rounded-xl bg-linear-to-r from-rose-600 to-red-600 px-6 py-2.5 font-semibold text-white shadow-md shadow-rose-600/20 hover:from-rose-700 hover:to-red-700 transition-all" @click="confirmRemoveTask">Yes, Remove Task</button>
          </div>
        </div>
      </div>
    </template>  </section>
</template>
