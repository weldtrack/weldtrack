<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { CalendarCheck } from 'lucide-vue-next'
import { useBookingsStore } from '../../../../stores/bookings'
import { type BookingItem, type BookingStatus } from '../../../../types/bookings'
import { useInventoryStore } from '../../../../stores/inventory'
import { useModalStore } from '../../../../stores/modal'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
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
    (booking) => booking.status === 'pending' || booking.status === 'confirmed' || booking.status === 'in-progress',
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
const confirmedCount = computed(() => bookings.value.filter((booking) => booking.status === 'confirmed' || booking.status === 'in-progress').length)
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

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await Promise.all([bookingsStore.fetchBookings(), loadServicePrices()])
  } finally {
    isLoading.value = false
  }
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
      return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
    case 'in-progress':
      return 'bg-indigo-50 text-indigo-700 ring-indigo-200'
    case 'cancelled':
      return 'bg-red-50 text-red-800 ring-red-600/10'
    default:
      return 'bg-gray-50 text-gray-700 ring-gray-200'
  }
}

function formatDate(value: string) {
  if (!value) return 'Not scheduled'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Not scheduled'
  return date.toLocaleDateString('en-PH', {
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
  const bookingId = selectedBooking.value.id

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

function hasStaffMaterialSubmission(bookingId: string) {
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
  <section class="relative space-y-6">
    <LocalLoader v-if="isLoading" />
    <!-- List View -->
    <template v-if="!isApprovalModalOpen && !isCompleteModalOpen && !isCancelModalOpen">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex items-start gap-3">
          <div class="flex h-12 w-12 items-center justify-center">
            <CalendarCheck class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Booking Approval</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">Review customer requests and approve bookings</p>
          </div>
        </div>
      </div>

      <!-- Metric Summary Cards -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div class="rounded-xl border border-amber-200 bg-amber-50 p-5 dark:border-amber-900/50 dark:bg-amber-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300">Pending Bookings</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ pendingCount }}</p>
        </div>
        <div class="rounded-xl border border-sky-200 bg-sky-50 p-5 dark:border-sky-900/50 dark:bg-sky-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-300">Confirmed Bookings</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ confirmedCount }}</p>
        </div>
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-900/50 dark:bg-emerald-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">Completed Bookings</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ completedCount }}</p>
        </div>
      </div>

      <!-- Filter Controls Card -->
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div class="grid grid-cols-1 gap-3 lg:grid-cols-4">
          <div class="relative lg:col-span-2">
            <svg class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M11 18a7 7 0 100-14 7 7 0 000 14z" />
            </svg>
            <input 
              v-model="searchTerm" 
              type="text" 
              placeholder="Search service, email, or phone..."
              class="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-sky-500" 
            />
          </div>

          <select 
            v-model="dateFilter"
            class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 outline-none transition focus:border-sky-500 focus:bg-white dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
          >
            <option value="all">All Dates</option>
            <option value="today">Today</option>
            <option value="1">1 Day Ago</option>
            <option value="2">2 Days Ago</option>
            <option value="3">3 Days Ago</option>
            <option value="5">5 Days Ago</option>
            <option value="7">7 Days Ago</option>
          </select>

          <button 
            type="button"
            class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition dark:border-slate-800 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            @click="resetFilters"
          >
            Reset Filters
          </button>
        </div>
      </div>
      <!-- Desktop bookings table -->
      <div class="hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:block">
        <div class="overflow-x-auto">
          <table class="w-full min-w-[920px] table-fixed divide-y divide-slate-100 dark:divide-slate-800">
            <thead class="bg-slate-50 dark:bg-slate-800/80">
              <tr class="text-left">
                <th class="w-[24%] px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Customer</th>
                <th class="w-[22%] px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Booking</th>
                <th class="w-[16%] px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Schedule</th>
                <th class="w-[20%] px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Cost</th>
                <th class="w-[18%] px-5 py-4 text-right text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Status & Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-transparent dark:divide-slate-800">
              <tr v-if="filteredBookings.length === 0">
                <td colspan="5" class="px-5 py-12 text-center text-sm text-slate-500 dark:text-slate-400">No active bookings match the selected filters.</td>
              </tr>
              <tr v-for="booking in filteredBookings" :key="booking.id" class="align-top transition-colors hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                <td class="px-5 py-5">
                  <p class="break-all text-sm font-semibold text-slate-900 dark:text-slate-100">{{ booking.email }}</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ booking.phone || 'No phone provided' }}</p>
                  <p class="mt-2 break-all text-[11px] text-slate-400">#{{ booking.id }}</p>
                </td>
                <td class="px-5 py-5">
                  <p class="break-words text-sm font-semibold text-slate-800 dark:text-slate-200">{{ booking.projectType }}</p>
                  <p class="mt-1 line-clamp-2 break-words text-xs leading-relaxed text-slate-500 dark:text-slate-400">{{ booking.description || 'No project description.' }}</p>
                  <p class="mt-2 text-[11px] text-slate-400">Booked {{ formatDate(booking.createdDate ?? '') }}</p>
                </td>
                <td class="px-5 py-5">
                  <p class="text-sm font-medium text-slate-800 dark:text-slate-200">{{ booking.scheduleDate ? formatDate(booking.scheduleDate) : 'Waiting for approval' }}</p>
                  <p class="mt-1 text-xs text-slate-400">{{ booking.scheduleDate ? 'Approved schedule' : 'Schedule pending' }}</p>
                </td>
                <td class="px-5 py-5">
                  <div class="space-y-1.5 text-xs text-slate-500 dark:text-slate-400">
                    <div class="flex justify-between gap-3"><span>Labor</span><span class="font-medium text-slate-800 dark:text-slate-200">₱{{ getDisplayedLaborCost(booking).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</span></div>
                    <div class="flex justify-between gap-3"><span>Materials</span><span class="text-right font-medium text-slate-800 dark:text-slate-200">{{ booking.materialCost != null ? `₱${booking.materialCost.toLocaleString('en-PH', { minimumFractionDigits: 2 })}` : 'Pending' }}</span></div>
                    <div class="flex justify-between gap-3 border-t border-slate-100 pt-1.5 dark:border-slate-800"><span class="font-semibold">Total</span><span class="font-semibold text-slate-900 dark:text-slate-100">₱{{ (getDisplayedLaborCost(booking) + (booking.materialCost ?? 0)).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</span></div>
                    <p v-if="(booking.status === 'confirmed' || booking.status === 'in-progress') && !hasStaffMaterialSubmission(booking.id)"
                      class="pt-1 text-[11px] font-medium leading-snug text-amber-700 dark:text-amber-400">
                      Awaiting staff materials
                    </p>
                  </div>
                </td>
                <td class="px-5 py-5 text-right">
                  <span
                    class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset"
                    :class="getStatusClass(booking.status)">
                    {{ getStatusLabel(booking.status) }}
                  </span>
                  <div class="mt-3 flex flex-col items-stretch gap-2">
                    <button v-if="booking.status === 'pending'" type="button"
                      class="rounded-lg bg-sky-600 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-sky-700"
                      @click="openApprovalModal(booking)">
                      Approve
                    </button>
                    <button v-if="booking.status === 'confirmed' || booking.status === 'in-progress'" type="button"
                      class="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-emerald-700"
                      @click="openCompleteModal(booking)">
                      Complete
                    </button>
                    <button v-if="booking.status !== 'cancelled'" type="button"
                      class="rounded-lg border border-rose-200 px-3 py-2 text-xs font-semibold text-rose-600 transition-colors hover:bg-rose-50 dark:border-rose-900/60 dark:hover:bg-rose-950/40"
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

      <!-- Responsive booking cards -->
      <div class="grid gap-4 lg:hidden">
        <div v-if="filteredBookings.length === 0" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">No active bookings match the selected filters.</div>
        <article v-for="booking in filteredBookings" :key="`mobile-${booking.id}`" class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="p-4 sm:p-5">
            <div class="flex items-start justify-between gap-3 border-b border-slate-100 pb-4 dark:border-slate-800">
              <div class="min-w-0">
                <p class="break-words text-base font-semibold text-slate-900 dark:text-slate-100">{{ booking.projectType }}</p>
                <p class="mt-1 break-all text-xs text-slate-500 dark:text-slate-400">{{ booking.email }}</p>
              </div>
              <span class="shrink-0 rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset" :class="getStatusClass(booking.status)">{{ getStatusLabel(booking.status) }}</span>
            </div>

            <dl class="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div><dt class="text-xs text-slate-400">Contact</dt><dd class="mt-1 break-words font-medium text-slate-700 dark:text-slate-300">{{ booking.phone || 'Not provided' }}</dd></div>
              <div><dt class="text-xs text-slate-400">Booked on</dt><dd class="mt-1 font-medium text-slate-700 dark:text-slate-300">{{ formatDate(booking.createdDate ?? '') }}</dd></div>
              <div class="col-span-2"><dt class="text-xs text-slate-400">Schedule</dt><dd class="mt-1 font-medium text-slate-700 dark:text-slate-300">{{ booking.scheduleDate ? formatDate(booking.scheduleDate) : 'Waiting for approval' }}</dd></div>
            </dl>

            <div class="mt-4 rounded-xl bg-slate-50 p-3 text-sm dark:bg-slate-800/60">
              <div class="flex justify-between gap-4 text-slate-500 dark:text-slate-400"><span>Labor</span><span class="font-medium text-slate-800 dark:text-slate-200">₱{{ getDisplayedLaborCost(booking).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</span></div>
              <div class="mt-2 flex justify-between gap-4 border-t border-slate-200 pt-2 font-semibold dark:border-slate-700"><span class="text-slate-700 dark:text-slate-300">Current total</span><span class="text-slate-900 dark:text-slate-100">₱{{ (getDisplayedLaborCost(booking) + (booking.materialCost ?? 0)).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</span></div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 border-t border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/60">
            <button v-if="booking.status === 'pending'" type="button" class="rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-sky-700" @click="openApprovalModal(booking)">Approve</button>
            <button v-if="booking.status === 'confirmed' || booking.status === 'in-progress'" type="button" class="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700" @click="openCompleteModal(booking)">Complete</button>
            <button type="button" class="rounded-xl border border-rose-200 bg-white px-4 py-2.5 text-sm font-semibold text-rose-600 hover:bg-rose-50 dark:border-rose-900/60 dark:bg-slate-900 dark:hover:bg-rose-950/40" @click="openCancelModal(booking)">Cancel</button>
          </div>
        </article>
      </div>
    </template>

    <!-- Approve Modal View -->
    <template v-else-if="isApprovalModalOpen">
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">Approve Booking</h3>
            <p class="text-sm text-slate-500 mt-1">Review booking details</p>
          </div>
          <button 
            @click="closeApprovalModal" 
            class="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Cancel
          </button>
        </div>
        <div class="p-6 max-w-4xl">
          <div v-if="selectedBooking"
            class="mb-6 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-700">
            <p class="mb-2"><span class="font-semibold text-slate-900">Email:</span> {{ selectedBooking.email }}</p>
            <p class="mb-2"><span class="font-semibold text-slate-900">Service:</span> {{ selectedBooking.projectType }}</p>
            <p class="mb-2"><span class="font-semibold text-slate-900">Contact:</span> {{ selectedBooking.phone }}</p>
            <div
              v-if="selectedBooking.location && (selectedBooking.location.province || selectedBooking.location.municipality || selectedBooking.location.barangay || selectedBooking.location.house)"
              class="mt-4 pt-4 border-t border-slate-200">
              <p class="font-semibold text-slate-900 mb-1">Customer Address</p>
              <p class="text-sm text-slate-700">{{ selectedBooking.location.house ? selectedBooking.location.house + ', ' :
                '' }}{{ selectedBooking.location.barangay ? selectedBooking.location.barangay + ', ' : '' }}{{
                  selectedBooking.location.municipality ? selectedBooking.location.municipality + ', ' : '' }}{{
                  selectedBooking.location.province ? selectedBooking.location.province : '' }}</p>
            </div>
            <div v-if="selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length" class="mt-4 pt-4 border-t border-slate-200">
              <p class="font-semibold text-slate-900">Field Images</p>
              <div class="mt-3 grid grid-cols-2 gap-4">
                <div v-if="selectedBooking.beforeImages?.length">
                  <p class="text-xs text-slate-600 mb-2 font-medium">Before</p>
                  <div class="flex flex-wrap gap-2">
                    <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`before-${idx}`" :href="img" target="_blank"
                      rel="noreferrer">
                      <img :src="img" class="h-24 w-32 rounded-xl border border-slate-200 object-cover shadow-sm transition-transform hover:scale-105" />
                    </a>
                  </div>
                </div>

                <div v-if="selectedBooking.afterImages?.length">
                  <p class="text-xs text-slate-600 mb-2 font-medium">After</p>
                  <div class="flex flex-wrap gap-2">
                    <a v-for="(img, idx) in selectedBooking.afterImages" :key="`after-${idx}`" :href="img" target="_blank"
                      rel="noreferrer">
                      <img :src="img" class="h-24 w-32 rounded-xl border border-slate-200 object-cover shadow-sm transition-transform hover:scale-105" />
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="scheduleDate">Schedule Date <span class="text-red-500">*</span><InfoTooltip text="Please provide the schedule date." /></label>
              <input id="scheduleDate" v-model="approvalForm.scheduleDate" type="date" :min="minDate" :max="maxDate"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
            </div>
          </div>

          <div class="mt-8 pt-5 border-t border-slate-100 flex justify-end gap-3">
            <button type="button"
              class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
              @click="closeApprovalModal">
              Cancel
            </button>
            <button type="button"
              class="rounded-xl bg-linear-to-r from-sky-600 to-sky-700 px-6 py-2.5 font-semibold text-white shadow-md shadow-sky-600/20 hover:from-sky-700 hover:to-sky-800 transition-all"
              @click="confirmApproval">
              Approve Booking
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Complete Modal View -->
    <template v-else-if="isCompleteModalOpen">
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">Complete Booking</h3>
            <p class="text-sm text-slate-500 mt-1">Finalize costs and status</p>
          </div>
          <button 
            @click="closeCompleteModal" 
            class="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Cancel
          </button>
        </div>
        <div class="p-6 max-w-4xl">
          <div v-if="selectedBooking"
            class="mb-6 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-700">
            <p class="mb-2"><span class="font-semibold text-slate-900">Email:</span> {{ selectedBooking.email }}</p>
            <p class="mb-2"><span class="font-semibold text-slate-900">Service:</span> {{ selectedBooking.projectType }}</p>
            <p><span class="font-semibold text-slate-900">Contact:</span> {{ selectedBooking.phone }}</p>
          </div>

          <div v-if="selectedBooking && (selectedBooking.beforeImages?.length || selectedBooking.afterImages?.length)"
            class="mb-6 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-700">
            <p class="font-semibold text-slate-900 mb-3">Field Images</p>
            <div class="grid grid-cols-2 gap-4">
              <div v-if="selectedBooking.beforeImages?.length">
                <p class="text-xs text-slate-600 mb-2 font-medium">Before</p>
                <div class="flex flex-wrap gap-2">
                  <a v-for="(img, idx) in selectedBooking.beforeImages" :key="`c-before-${idx}`" :href="img" target="_blank"
                    rel="noreferrer">
                    <img :src="img" class="h-24 w-32 rounded-xl border border-slate-200 object-cover shadow-sm transition-transform hover:scale-105" />
                  </a>
                </div>
              </div>
              <div v-if="selectedBooking.afterImages?.length">
                <p class="text-xs text-slate-600 mb-2 font-medium">After</p>
                <div class="flex flex-wrap gap-2">
                  <a v-for="(img, idx) in selectedBooking.afterImages" :key="`c-after-${idx}`" :href="img" target="_blank"
                    rel="noreferrer">
                    <img :src="img" class="h-24 w-32 rounded-xl border border-slate-200 object-cover shadow-sm transition-transform hover:scale-105" />
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div class="rounded-xl bg-slate-50 p-4 border border-slate-100 flex justify-between items-center">
              <p class="text-sm font-medium text-gray-600">Labor Cost /hour</p>
              <p class="text-xl font-bold text-gray-900">₱{{ (selectedBooking ?
                getDisplayedLaborCost(selectedBooking) :
                0).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
            </div>

            <div v-if="selectedBooking && !hasStaffMaterialSubmission(selectedBooking.id)"
              class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800 flex items-center gap-2">
              <svg class="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              Staff has not submitted materials for this booking yet.
            </div>

            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="materialCost">Material Cost<InfoTooltip text="Please provide the material cost." /></label>
              <div class="flex flex-col sm:flex-row gap-3">
                <input id="materialCost" v-model="completionForm.materialCost" type="number" min="0"
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-200" />
                <button type="button"
                  class="whitespace-nowrap rounded-xl bg-amber-100 px-5 py-3 font-semibold text-amber-800 hover:bg-amber-200 transition-colors"
                  @click="loadMaterialsForBooking">Load from recorded materials</button>
              </div>
            </div>

            <div class="rounded-xl bg-slate-800 p-5 text-white flex justify-between items-center shadow-md">
              <p class="text-sm font-medium text-slate-300">Total Price</p>
              <p class="text-2xl font-bold">₱{{ computedCompletionTotal.toLocaleString('en-PH', {
                minimumFractionDigits: 2
              }) }}</p>
            </div>
          </div>

          <div class="mt-8 pt-5 border-t border-slate-100 flex justify-end gap-3">
            <button type="button"
              class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
              @click="closeCompleteModal">
              Cancel
            </button>
            <button type="button"
              class="rounded-xl bg-linear-to-r from-green-600 to-emerald-600 px-6 py-2.5 font-semibold text-white shadow-md shadow-green-600/20 hover:from-green-700 hover:to-emerald-700 transition-all"
              @click="confirmComplete">
              Mark Completed
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Cancel Modal View -->
    <template v-else-if="isCancelModalOpen">
      <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between bg-transparent">
          <div>
            <h3 class="text-xl font-bold text-slate-900">Cancel Booking</h3>
            <p class="text-sm text-slate-500 mt-1">Provide a cancellation reason</p>
          </div>
          <button 
            @click="closeCancelModal" 
            class="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Cancel
          </button>
        </div>
        <div class="p-6 max-w-2xl">
          <div class="space-y-4">
            <div>
              <label class="flex items-center text-sm font-semibold text-gray-700 mb-1.5" for="cancelReason">Cancel Reason <span class="text-red-500">*</span><InfoTooltip text="Please provide the cancel reason." /></label>
              <textarea id="cancelReason" v-model="cancelForm.reason" rows="5" placeholder="Enter cancellation reason..."
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200" />
            </div>
          </div>

          <div class="mt-8 pt-5 border-t border-slate-100 flex justify-end gap-3">
            <button type="button"
              class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
              @click="closeCancelModal">
              Back
            </button>
            <button type="button"
              class="rounded-xl bg-linear-to-r from-red-600 to-rose-600 px-6 py-2.5 font-semibold text-white shadow-md shadow-red-600/20 disabled:cursor-not-allowed disabled:opacity-50 transition-all"
              :disabled="!cancelForm.reason.trim()" @click="cancelBookingAsAdmin">
              Confirm Cancel
            </button>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
