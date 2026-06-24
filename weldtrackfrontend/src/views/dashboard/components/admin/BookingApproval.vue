<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { CalendarCheck } from 'lucide-vue-next'
import { useBookingsStore } from '../../../../stores/bookings'
import { type BookingItem, type BookingStatus } from '../../../../types/bookings'
import { useInventoryStore } from '../../../../stores/inventory'
import { useModalStore } from '../../../../stores/modal'
import ModalShell from '../../../../components/ui/ModalShell.vue'
import { getUserFriendlyApiError } from '../../../../services/errorMessage'
import api from '../../../../api/api'

const bookingsStore = useBookingsStore()
const inventoryStore = useInventoryStore()
const modalStore = useModalStore()
const bookings = computed(() => bookingsStore.bookings)

const searchTerm = ref('')
const dateFilter = ref('all')

const filteredBookings = computed(() => {
  let data = bookings.value.filter(
    (booking) => booking.status === 'pending' || booking.status === 'confirmed',
  )

  const query = searchTerm.value.trim().toLowerCase()

  if (query) {
    data = data.filter(
      (booking) =>
        booking.projectType?.toLowerCase().includes(query) ||
        booking.email?.toLowerCase().includes(query) ||
        booking.phone?.toLowerCase().includes(query),
    )
  }

  if (dateFilter.value !== 'all') {
    const today = new Date()

    data = data.filter((booking) => {
      const created = new Date(booking.createdDate ?? '')
      const diffDays = Math.floor(
        (today.getTime() - created.getTime()) / (1000 * 60 * 60 * 24),
      )

      switch (dateFilter.value) {
        case 'today':
          return diffDays === 0
        case '1':
          return diffDays === 1

        case '2':
          return diffDays === 2

        case '3':
          return diffDays === 3

        case '5':
          return diffDays === 5

        case '7':
          return diffDays === 7
        default:
          return true
      }
    })
  }

  return data
})

function resetFilters() {
  searchTerm.value = ''
  dateFilter.value = 'all'
}

const pendingCount = computed(() => bookings.value.filter((booking) => booking.status === 'pending').length)
const confirmedCount = computed(() => bookings.value.filter((booking) => booking.status === 'confirmed').length)
const completedCount = computed(() => bookings.value.filter((booking) => booking.status === 'completed').length)

const isApprovalModalOpen = ref(false)
const selectedBooking = ref<BookingItem | null>(null)
const approvalForm = reactive({
  scheduleDate: '',
})
const isCompleteModalOpen = ref(false)
const completionForm = reactive({
  materialCost: '',
})
const isCancelModalOpen = ref(false)
const cancelForm = reactive({
  reason: '',
})
const servicePriceMap = ref<Record<string, number>>({})

// --- DATE RESTRICTION LOGIC ---

// Blocks any date before today
const minDate = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Blocks any date further than 1 month from today
const maxDate = computed(() => {
  const date = new Date()
  date.setMonth(date.getMonth() + 1)
  return date.toISOString().split('T')[0]
})

// ------------------------------

function normalizeServiceName(value: string) {
  return value.trim().toLowerCase()
}

function getLaborPriceFor(projectType: string) {
  return servicePriceMap.value[normalizeServiceName(projectType)] ?? 0
}

async function loadServicePrices() {
  try {
    const response = await api.get('/services')
    const services = Array.isArray(response.data)
      ? response.data
      : response.data?.data ?? response.data?.services ?? []

    servicePriceMap.value = services.reduce((acc: Record<string, number>, service: any) => {
      const name = String(service.name ?? service.serviceName ?? service.title ?? '').trim()
      if (!name) return acc
      acc[normalizeServiceName(name)] = Number(service.price ?? service.laborPrice ?? service.labor_price ?? 0)
      return acc
    }, {})
  } catch (err) {
    console.error('Failed to fetch service price:', err)
    servicePriceMap.value = {}
  }
}

onMounted(() => {
  void bookingsStore.fetchBookings()
  void loadServicePrices()
})

function getStatusLabel(status: BookingStatus) {
  switch (status) {
    case 'pending':
      return 'Pending'
    case 'confirmed':
      return 'Confirmed'
    case 'completed':
      return 'Completed'
    case 'cancelled':
      return 'Cancelled'
    default:
      return status
  }
}

function getStatusClass(status: BookingStatus) {
  switch (status) {
    case 'pending':
      return 'bg-yellow-50 text-yellow-800 ring-yellow-600/20'
    case 'confirmed':
      return 'bg-blue-50 text-blue-800 ring-blue-600/20'
    case 'completed':
      return 'bg-green-50 text-green-800 ring-green-600/20'
    case 'cancelled':
      return 'bg-red-50 text-red-800 ring-red-600/10'
    default:
      return 'bg-gray-50 text-gray-700 ring-gray-600/10'
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function openApprovalModal(booking: BookingItem) {
  selectedBooking.value = booking
  approvalForm.scheduleDate = String(booking.scheduleDate ?? booking.preferredDate ?? '')
  if (!Object.keys(servicePriceMap.value).length) {
    await loadServicePrices()
  }
  isApprovalModalOpen.value = true
}

function openCompleteModal(booking: BookingItem) {
  selectedBooking.value = booking
  completionForm.materialCost = booking.materialCost ? String(booking.materialCost) : ''
  isCompleteModalOpen.value = true
  inventoryStore.fetchMovements().then(() => loadMaterialsForBooking())
}

function closeCompleteModal() {
  isCompleteModalOpen.value = false
  selectedBooking.value = null
  completionForm.materialCost = ''
}

function closeApprovalModal() {
  isApprovalModalOpen.value = false
  selectedBooking.value = null
  approvalForm.scheduleDate = ''
}

function openCancelModal(booking: BookingItem) {
  selectedBooking.value = booking
  cancelForm.reason = booking.cancelReason || ''
  isCancelModalOpen.value = true
}

function closeCancelModal() {
  isCancelModalOpen.value = false
  selectedBooking.value = null
  cancelForm.reason = ''
}

async function confirmApproval() {
  if (!selectedBooking.value) return

  // Guard Clauses for strict date enforcement
  if (!approvalForm.scheduleDate) {
    modalStore.open({
      title: 'Missing Date',
      message: 'Please pick a schedule date before confirming.',
      variant: 'error',
    })
    return
  }

  if (approvalForm.scheduleDate < minDate.value || approvalForm.scheduleDate > maxDate.value) {
    modalStore.open({
      title: 'Invalid Date Choice',
      message: 'The selected date falls outside the allowed limits (Today up to 1 month ahead).',
      variant: 'error',
    })
    return
  }

  const patch = {
    scheduleDate: approvalForm.scheduleDate,
    estimatedCost: getLaborPriceFor(selectedBooking.value.projectType),
    status: 'confirmed' as BookingStatus,
  }

  await bookingsStore.updateBooking(selectedBooking.value.id, patch)
  closeApprovalModal()
}

async function cancelBookingAsAdmin() {
  if (!selectedBooking.value) return
  if (!cancelForm.reason.trim()) return
  const patch = {
    status: 'cancelled' as BookingStatus,
    cancelReason: cancelForm.reason.trim(),
    cancelledBy: 'admin' as const,
  }
  await bookingsStore.updateBooking(selectedBooking.value.id, patch)
  closeCancelModal()
}

const computedCompletionTotal = computed(() => {
  if (!selectedBooking.value) return 0
  const labor = selectedBooking.value.estimatedCost || getLaborPriceFor(selectedBooking.value.projectType)
  const mat = Number(completionForm.materialCost) || 0
  return labor + mat
})

async function confirmComplete() {
  if (!selectedBooking.value) return

  if (!hasStaffMaterialSubmission(selectedBooking.value.id)) {
    modalStore.open({
      title: 'No materials recorded',
      message: 'Staff has not submitted any recorded materials for this booking. Are you sure you want to complete it without material records?',
      variant: 'warning',
      confirmLabel: 'Complete Anyway',
      cancelLabel: 'Cancel',
      onConfirm: () => completeBookingForce(),
    })
    return
  }

  completeBookingForce()
}

async function completeBookingForce() {
  if (!selectedBooking.value) return
  const labor = selectedBooking.value.estimatedCost || getLaborPriceFor(selectedBooking.value.projectType)
  const material = Number(completionForm.materialCost) || 0
  const patch = {
    status: 'completed' as BookingStatus,
    estimatedCost: labor,
    materialCost: material,
    totalPrice: labor + material,
  }

  await bookingsStore.updateBooking(selectedBooking.value.id, patch)
  closeCompleteModal()
}

async function loadMaterialsForBooking() {
  if (!selectedBooking.value) return
  const bookingId = Number(selectedBooking.value.id)

  try {
    const remote = await bookingsStore.getBooking(bookingId)
    if (remote && Array.isArray(remote.materials)) {
      const total = remote.materials.reduce((acc, line) => {
        const subtotal = Number(line.subtotal ?? 0)
        if (subtotal > 0) return acc + subtotal
        return acc + Number(line.unitPrice ?? 0) * Number(line.qty ?? 0)
      }, 0)

      if (total > 0) {
        completionForm.materialCost = String(total)
        return
      }
    }
  } catch (err) {
    modalStore.open({
      title: 'Error',
      message: getUserFriendlyApiError(err),
      variant: 'error',
    })
  }

  try {
    await inventoryStore.fetchMovements({ bookingId })
  } catch (err) {
    modalStore.open({
      title: 'Error',
      message: getUserFriendlyApiError(err),
      variant: 'error',
    })
    return
  }
  const movements = inventoryStore.getMovementsForBooking(bookingId)

  let total = 0
  movements.forEach((m) => {
    if (m.type === 'stock-out') {
      const item = inventoryStore.items.find((it) => it.id === m.itemId)
      if (item) {
        const lineTotal = m.quantity * item.unitPrice
        total += lineTotal
      }
    }
  })
  completionForm.materialCost = String(total)
}

function hasStaffMaterialSubmission(bookingId: number) {
  const hasMovements = inventoryStore.getMovementsForBooking(bookingId).some((m) => m.type === 'stock-out')
  const booking = bookingsStore.bookings.find((b) => b.id === bookingId)
  const hasImages = Boolean(booking && ((booking.beforeImages && booking.beforeImages.length > 0) || (booking.afterImages && booking.afterImages.length > 0)))
  return hasMovements || hasImages
}

function getDisplayedLaborCost(booking: BookingItem) {
  return booking.estimatedCost && booking.estimatedCost > 0 ? booking.estimatedCost : getLaborPriceFor(booking.projectType)
}
</script>

<template>
  <section class="space-y-6 rounded-lg border border-gray-200 bg-white p-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-3">
        <div
          class="flex h-10 w-10 items-center justify-center rounded-lg bg-linear-to-br from-sky-50 to-sky ring-1 ring-sky-100">
          <CalendarCheck class="h-5 w-5 text-sky-600" />
        </div>
        <div>
          <h2 class="text-2xl font-semibold text-gray-900">Booking Approval</h2>
          <p class="mt-1 text-gray-600">Review customer requests and approve bookings</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-lg bg-sky-50 p-4">
        <p class="text-xs uppercase tracking-wide text-sky-600">Pending</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ pendingCount }}</p>
      </div>
      <div class="rounded-lg bg-sky-50 p-4">
        <p class="text-xs uppercase tracking-wide text-sky-600">Confirmed</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ confirmedCount }}</p>
      </div>
      <div class="rounded-lg bg-sky-50 p-4">
        <p class="text-xs uppercase tracking-wide text-sky-600">Completed</p>
        <p class="mt-1 text-2xl font-bold text-gray-900">{{ completedCount }}</p>
      </div>
    </div>

    <div class="rounded-xl border border-gray-200 bg-white p-4">
      <div class="grid grid-cols-1 gap-3 lg:grid-cols-4">
        <div class="relative lg:col-span-2">
          <svg class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 21l-4.35-4.35M11 18a7 7 0 100-14 7 7 0 000 14z" />
          </svg>

          <input v-model="searchTerm" type="text" placeholder="Search service, email, or phone..."
            class="w-full rounded-xl border border-gray-300 bg-gray-50 py-3 pl-10 pr-4 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200" />
        </div>

        <select v-model="dateFilter"
          class="rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200">
          <option value="all">All Dates</option>
          <option value="today">Today</option>
          <option value="1">1 Day Ago</option>
          <option value="2">2 Days Ago</option>
          <option value="3">3 Days Ago</option>
          <option value="5">5 Days Ago</option>
          <option value="7">7 Days Ago</option>
        </select>

        <button type="button"
          class="rounded-xl border border-gray-300 px-4 py-3 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          @click="resetFilters">
          Reset Filters
        </button>
      </div>
    </div>
    <div class="overflow-hidden rounded-xl border border-gray-200">
      <div class="h-screen overflow-x-auto">
        <table class="w-full min-w-300 divide-y divide-gray-200">
          <thead class="bg-gray-50/70">
            <tr class="text-left">
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Email/Contact No.</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Service</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Booked On</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Schedule</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Cost Summary</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500">Status</th>
              <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-500 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 bg-white">
            <tr v-for="booking in filteredBookings" :key="booking.id" class="transition-colors hover:bg-slate-50/80">
              <td class="px-6 py-4 font-medium text-gray-900 wrap-break-word">{{ booking.email }}<p
                  class="mt-0.5 text-xs text-gray-500">{{ booking.phone }}</p>
              </td>
              <td class="px-6 py-4 text-gray-700 whitespace-nowrap">
                <p>{{ booking.projectType }}</p>
              </td>
              <td class="px-6 py-4 text-gray-600 whitespace-nowrap">{{ formatDate(booking.createdDate ?? '') }}</td>
              <td class="px-6 py-4 text-gray-700 whitespace-nowrap">{{ booking.scheduleDate || 'Waiting for approval' }}
              </td>
              <td class="px-6 py-4 text-gray-900">
                <div class="space-y-1 text-sm">
                  <p>Labor: ₱{{ getDisplayedLaborCost(booking).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
                  </p>
                  <p>Material: <span v-if="booking.materialCost != null">₱{{
                    booking.materialCost.toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</span><span v-else
                      class="text-gray-500">After completion</span></p>
                  <p class="font-semibold">Total: ₱{{ (getDisplayedLaborCost(booking) + (booking.materialCost ??
                    0)).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
                  <p v-if="booking.status === 'confirmed' && !hasStaffMaterialSubmission(booking.id)"
                    class="text-xs font-semibold text-amber-700">
                    Staff materials not submitted yet
                  </p>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset whitespace-nowrap"
                  :class="getStatusClass(booking.status)">
                  {{ getStatusLabel(booking.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-wrap gap-2">
                  <button v-if="booking.status === 'pending'" type="button"
                    class="rounded-lg bg-sky-600 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-700 transition-colors"
                    @click="openApprovalModal(booking)">
                    Approve
                  </button>
                  <button v-if="booking.status === 'confirmed'" type="button"
                    class="rounded-lg bg-green-600 px-3 py-2 text-sm font-semibold text-white hover:bg-green-700 transition-colors"
                    @click="openCompleteModal(booking)">
                    Complete
                  </button>
                  <button v-if="booking.status !== 'cancelled'" type="button"
                    class="rounded-lg border border-red-300 px-3 py-2 text-sm font-semibold text-red-600 hover:bg-red-50 transition-colors"
                    @click="openCancelModal(booking)">
                    Cancel
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <ModalShell :show="isApprovalModalOpen" title="Approve Booking" subtitle="Review booking details" tone="blue"
      size="xl" @close="closeApprovalModal">
      <div v-if="selectedBooking"
        class="mb-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <p><span class="font-semibold text-slate-900">Email:</span> {{ selectedBooking.email }}</p>
        <p><span class="font-semibold text-slate-900">Service:</span> {{ selectedBooking.projectType }}</p>
        <p><span class="font-semibold text-slate-900">Contact:</span> {{ selectedBooking.phone }}</p>
        <div
          v-if="selectedBooking.location && (selectedBooking.location.province || selectedBooking.location.municipality || selectedBooking.location.barangay || selectedBooking.location.house)"
          class="mt-2">
          <p class="font-semibold text-slate-900">Customer Address</p>
          <p class="text-sm text-slate-700">{{ selectedBooking.location.house ? selectedBooking.location.house + ', ' :
            '' }}{{ selectedBooking.location.barangay ? selectedBooking.location.barangay + ', ' : '' }}{{
              selectedBooking.location.municipality ? selectedBooking.location.municipality + ', ' : '' }}{{
              selectedBooking.location.province ? selectedBooking.location.province : '' }}</p>
        </div>
        <div v-if="selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length" class="mt-3">
          <p class="font-semibold text-slate-900">Field Images</p>
          <div class="mt-2 grid grid-cols-2 gap-2">
            <div v-if="selectedBooking.beforeImages?.length">
              <p class="text-xs text-slate-600">Before</p>
              <div class="mt-1 flex flex-wrap gap-2">
                <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`before-${idx}`" :href="img" target="_blank"
                  rel="noreferrer">
                  <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
                </a>
              </div>
            </div>

            <div v-if="selectedBooking.afterImages?.length">
              <p class="text-xs text-slate-600">After</p>
              <div class="mt-1 flex flex-wrap gap-2">
                <a v-for="(img, idx) in selectedBooking.afterImages" :key="`after-${idx}`" :href="img" target="_blank"
                  rel="noreferrer">
                  <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700" for="scheduleDate">Schedule Date</label>
          <input id="scheduleDate" v-model="approvalForm.scheduleDate" type="date" :min="minDate" :max="maxDate"
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
        </div>
      </div>

      <template #footer>
        <button type="button"
          class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
          @click="closeApprovalModal">
          Cancel
        </button>
        <button type="button"
          class="rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-4 py-3 font-semibold text-white shadow-lg shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800"
          @click="confirmApproval">
          Approve Booking
        </button>
      </template>
    </ModalShell>

    <ModalShell :show="isCompleteModalOpen" title="Complete Booking" subtitle="Finalize costs and status" tone="green"
      size="lg" @close="closeCompleteModal">
      <div v-if="selectedBooking"
        class="mb-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <p><span class="font-semibold text-slate-900">Email:</span> {{ selectedBooking.email }}</p>
        <p><span class="font-semibold text-slate-900">Service:</span> {{ selectedBooking.projectType }}</p>
        <p><span class="font-semibold text-slate-900">Contact:</span> {{ selectedBooking.phone }}</p>
      </div>

      <div v-if="selectedBooking && (selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length)"
        class="mb-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <p class="font-semibold text-slate-900">Field Images</p>
        <div class="mt-2 grid grid-cols-2 gap-2">
          <div v-if="selectedBooking.beforeImages?.length">
            <p class="text-xs text-slate-600">Before</p>
            <div class="mt-1 flex flex-wrap gap-2">
              <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`c-before-${idx}`" :href="img" target="_blank"
                rel="noreferrer">
                <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
              </a>
            </div>
          </div>
          <div v-if="selectedBooking.afterImages?.length">
            <p class="text-xs text-slate-600">After</p>
            <div class="mt-1 flex flex-wrap gap-2">
              <a v-for="(img, idx) in selectedBooking.afterImages" :key="`c-after-${idx}`" :href="img" target="_blank"
                rel="noreferrer">
                <img :src="img" class="h-20 w-28 rounded-xl border border-slate-200 object-cover shadow-sm" />
              </a>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div>
          <p class="text-sm text-gray-600">Labor Cost</p>
          <p class="mt-1 text-lg font-medium text-gray-900">₱{{ (selectedBooking ?
            getDisplayedLaborCost(selectedBooking) :
            0).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
        </div>

        <div v-if="selectedBooking && !hasStaffMaterialSubmission(selectedBooking.id)"
          class="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800">
          Staff has not submitted materials for this booking yet.
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700" for="materialCost">Material Cost</label>
          <div class="flex gap-2">
            <input id="materialCost" v-model="completionForm.materialCost" type="number" min="0"
              class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200" />
            <button type="button"
              class="mt-1 rounded-xl bg-amber-100 px-3 py-2 font-semibold text-amber-800 hover:bg-amber-200"
              @click="loadMaterialsForBooking">Load from recorded materials</button>
          </div>
        </div>

        <div>
          <p class="text-sm text-gray-600">Total Price</p>
          <p class="mt-1 text-lg font-medium text-gray-900">₱{{ computedCompletionTotal.toLocaleString('en-PH', {
            minimumFractionDigits: 2
          }) }}</p>
        </div>
      </div>

      <template #footer>
        <button type="button"
          class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
          @click="closeCompleteModal">
          Cancel
        </button>
        <button type="button"
          class="rounded-xl bg-linear-to-r from-green-600 to-emerald-600 px-4 py-3 font-semibold text-white shadow-lg shadow-green-600/20 hover:from-green-700 hover:to-emerald-700"
          @click="confirmComplete">
          Mark Completed
        </button>
      </template>
    </ModalShell>

    <ModalShell :show="isCancelModalOpen" title="Cancel Booking" subtitle="Provide a cancellation reason" tone="red"
      size="lg" @close="closeCancelModal">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700" for="cancelReason">Cancel Reason</label>
          <textarea id="cancelReason" v-model="cancelForm.reason" rows="4" placeholder="Enter cancellation reason..."
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200" />
        </div>
      </div>

      <template #footer>
        <button type="button"
          class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
          @click="closeCancelModal">
          Back
        </button>
        <button type="button"
          class="rounded-xl bg-linear-to-r from-red-600 to-rose-600 px-4 py-3 font-semibold text-white shadow-lg shadow-red-600/20 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="!cancelForm.reason.trim()" @click="cancelBookingAsAdmin">
          Confirm Cancel
        </button>
      </template>
    </ModalShell>
  </section>
</template>