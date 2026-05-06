<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '../../../stores/auth'
import { useBookingsStore, type BookingItem } from '../../../stores/bookings'

const auth = useAuthStore()
const bookingsStore = useBookingsStore()

const userRole = computed(() => auth.role || 'customer')
const currentUser = computed(() => auth.email || 'User')
const currentEmail = computed(() => auth.email || '')

const isDialogOpen = ref(false)
const isCancelModalOpen = ref(false)
const selectedBooking = ref<BookingItem | null>(null)

const formData = reactive({
  customerName: '',
  email: '',
  phone: '',
  projectType: '',
  description: '',
  createdDate: '',
})

const cancelForm = reactive({
  reason: '',
})

const projectTypes = [
  'Gate Welding',
  'Metal Railings',
  'Steel Frame Construction',
  'Staircase Fabrication',
  'Metal Doors & Windows',
  'Pipe & Duct Welding',
  'Metal Shelving',
  'Automotive Welding',
  'Fence Installation',
  'Tank & Vessel Fabrication',
  'Repair & Maintenance',
  'Other',
]

const laborPriceMap: Record<string, number> = {
  'Gate Welding': 4000,
  'Metal Railings': 6000,
  'Steel Frame Construction': 60000,
  'Staircase Fabrication': 5000,
  'Metal Doors & Windows': 5000,
  'Pipe & Duct Welding': 4000,
  'Metal Shelving': 7000,
  'Automotive Welding': 10000,
  'Fence Installation': 5000,
  'Tank & Vessel Fabrication': 10000,
  'Repair & Maintenance': 6000,
  Other: 0,
}

const selectedLaborPrice = computed(() => {
  return laborPriceMap[formData.projectType] ?? 0
})

const selectedTotalCost = computed(() => selectedLaborPrice.value)

const filteredBookings = computed(() => {
  const bookings = Array.isArray(bookingsStore.bookings) ? bookingsStore.bookings : []

  if (userRole.value !== 'customer') return bookings
  return bookings.filter((b) => b.email === currentEmail.value || b.customerName === currentUser.value)
})
const activeBookings = computed(() =>
  filteredBookings.value.filter((booking) => booking.status === 'pending' || booking.status === 'confirmed'),
)

const pendingCount = computed(() => filteredBookings.value.filter((b) => b.status === 'pending').length)
const confirmedCount = computed(() => filteredBookings.value.filter((b) => b.status === 'confirmed').length)

onMounted(() => {
  bookingsStore.fetchBookings().catch(() => {
    // keep seeded local data if the API is unavailable
  })
})


function resetForm() {
  formData.customerName = userRole.value === 'customer' ? currentUser.value : ''
  formData.email = userRole.value === 'customer' ? currentEmail.value : ''
  formData.phone = ''
  formData.projectType = ''
  formData.description = ''
  formData.createdDate = new Date().toISOString().split('T')[0]
}

function closeDialog() {
  isDialogOpen.value = false
  resetForm()
}

function openDialog() {
  resetForm()
  isDialogOpen.value = true
}

async function handleSubmit() {
  await bookingsStore.createBooking({
    customerName: formData.customerName,
    email: formData.email,
    phone: formData.phone,
    projectType: formData.projectType,
    description: formData.description,
    status: 'pending',
    createdDate: formData.createdDate,
    preferredDate: formData.createdDate,
  })

  closeDialog()
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

function cancelAsCustomer() {
  if (!selectedBooking.value) return
  if (selectedBooking.value.status !== 'pending') return
  if (!cancelForm.reason.trim()) return

  selectedBooking.value.status = 'cancelled'
  selectedBooking.value.cancelReason = cancelForm.reason.trim()
  selectedBooking.value.cancelledBy = 'customer'
  closeCancelModal()
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function getLaborCost(projectType: string) {
  return laborPriceMap[projectType] ?? 0
}

function getMaterialCostMessage(booking: BookingItem) {
  if (booking.status !== 'completed') {
    return 'Material cost will be displayed after project completion.'
  }

  if (booking.materialCost == null) {
    return 'Material cost will be added after project completion.'
  }

  return formatCurrency(booking.materialCost)
}

function getTotalCost(booking: BookingItem) {
  return getLaborCost(booking.projectType) + (booking.materialCost ?? 0)
}

function getScheduleMessage(booking: BookingItem) {
  if (booking.status === 'pending') {
    return 'Waiting for approval'
  }

  if (booking.scheduleDate) {
    return formatDate(booking.scheduleDate)
  }

  return 'To be scheduled'
}

function formatCreatedDate(value?: string) {
  return value ? formatDate(value) : '-'
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h3 class="mb-1 text-2xl font-semibold text-gray-900">My Bookings</h3>
        <p class="text-sm text-gray-600">Book welding services and track your projects</p>
      </div>

      <button
        type="button"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
        @click="openDialog"
      >
        <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Booking
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
        <p class="text-sm font-medium text-yellow-700">Pending</p>
        <p class="mt-1 text-2xl font-bold text-yellow-900">{{ pendingCount }}</p>
      </div>
      <div class="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <p class="text-sm font-medium text-blue-700">Approved</p>
        <p class="mt-1 text-2xl font-bold text-blue-900">{{ confirmedCount }}</p>
      </div>
      <div class="rounded-lg border border-purple-200 bg-purple-50 p-4">
        <p class="text-sm font-medium text-purple-700">Total</p>
        <p class="mt-1 text-2xl font-bold text-purple-900">{{ filteredBookings.length }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-2">
      <div v-if="activeBookings.length === 0" class="col-span-full rounded-lg border border-gray-200 bg-gray-50 p-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-4 text-gray-600">No active bookings yet</p>
      </div>

      <div v-for="booking in activeBookings" :key="booking.id" class="overflow-hidden rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
        <div class="mb-4 flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3">
              <h3 class="text-lg font-semibold text-gray-900">{{ booking.projectType }}</h3>
              <span :class="['rounded-full border px-3 py-1 text-xs font-medium capitalize', booking.status === 'pending' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' : booking.status === 'confirmed' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-green-50 text-green-700 border-green-200']">
                {{ booking.status }}
              </span>
            </div>
            <p class="mt-2 text-sm text-gray-600">{{ booking.description }}</p>
          </div>
        </div>

        <div class="grid gap-3 text-sm sm:grid-cols-2">
          <div class="rounded-lg bg-blue-50 border border-blue-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-blue-600 font-medium">Email</p>
            <p class="mt-1 text-gray-900 font-medium">{{ booking.email }}</p>
          </div>

          <div class="rounded-lg bg-green-50 border border-green-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-green-600 font-medium">Phone</p>
            <p class="mt-1 text-gray-900 font-medium">{{ booking.phone }}</p>
          </div>

          <div class="rounded-lg bg-purple-50 border border-purple-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-purple-600 font-medium">Schedule</p>
            <p class="mt-1 text-gray-900 font-medium">{{ getScheduleMessage(booking) }}</p>
          </div>

          <div class="rounded-lg bg-orange-50 border border-orange-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-orange-600 font-medium">Booked On</p>
            <p class="mt-1 text-gray-900 font-medium">{{ formatCreatedDate(booking.createdDate) }}</p>
          </div>

          <div class="rounded-lg bg-indigo-50 border border-indigo-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-indigo-600 font-medium">Labor Cost</p>
            <p class="mt-1 text-gray-900 font-medium">{{ formatCurrency(getLaborCost(booking.projectType)) }}</p>
          </div>

          <div class="rounded-lg bg-pink-50 border border-pink-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-pink-600 font-medium">Material Cost</p>
            <p class="mt-1 text-gray-900 font-medium text-xs">{{ getMaterialCostMessage(booking) }}</p>
          </div>

          <div class="rounded-lg bg-cyan-50 border border-cyan-200 px-3 py-2 sm:col-span-2">
            <p class="text-xs uppercase tracking-wide text-cyan-600 font-medium">Total Cost</p>
            <p class="mt-1 text-lg font-bold text-cyan-900">{{ formatCurrency(getTotalCost(booking)) }}</p>
          </div>
        </div>

        <div class="mt-4 flex gap-2" v-if="booking.status === 'pending'">
          <button
            type="button"
            class="rounded-lg border border-red-300 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-50"
            @click="openCancelModal(booking)"
          >
            Cancel Booking
          </button>
        </div>
      </div>
    </div>

    <div v-if="isDialogOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="closeDialog">
      <div class="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl">
        <div class="mb-5">
          <h4 class="text-lg font-semibold text-gray-900">Create New Booking</h4>
        </div>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="createdDate">Booked On</label>
            <input id="createdDate" v-model="formData.createdDate" type="date" readonly class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-100 px-4 py-3" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700" for="email">Email</label>
            <input id="email" v-model="formData.email" type="email" readonly required class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-100 px-4 py-3" />
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700" for="phone">Phone Number</label>
              <input id="phone" v-model="formData.phone" type="tel" required class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700" for="projectType">Project Type</label>
              <select id="projectType" v-model="formData.projectType" required class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3">
                <option value="">Select project type</option>
                <option v-for="type in projectTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>
          </div>

          <div class="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
            Material cost will be displayed after project completion.
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div class="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3">
              <p class="text-sm text-gray-600">Labor Cost</p>
              <p class="mt-1 text-lg font-semibold text-gray-900">{{ formatCurrency(selectedLaborPrice) }}</p>
            </div>
            <div class="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3">
              <p class="text-sm text-gray-600">Total Cost</p>
              <p class="mt-1 text-lg font-semibold text-gray-900">{{ formatCurrency(selectedTotalCost) }}</p>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700" for="description">Project Description</label>
            <textarea id="description" v-model="formData.description" required rows="4" placeholder="Describe your welding project requirements..." class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3" />
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" class="flex-1 rounded-lg border border-gray-300 px-4 py-3 font-semibold text-gray-700 hover:bg-gray-50" @click="closeDialog">Cancel</button>
            <button type="submit" class="flex-1 rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700">Submit Booking</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isCancelModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="closeCancelModal">
      <div class="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl">
        <h4 class="mb-4 text-lg font-semibold text-gray-900">Cancel Booking</h4>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="customerCancelReason">Cancel Reason</label>
            <textarea
              id="customerCancelReason"
              v-model="cancelForm.reason"
              rows="4"
              placeholder="Tell us why you are cancelling this booking..."
              class="mt-1 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3"
            />
          </div>
          <div class="flex gap-3 pt-2">
            <button type="button" class="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-semibold text-gray-700 hover:bg-gray-50" @click="closeCancelModal">Back</button>
            <button
              type="button"
              class="flex-1 rounded-lg bg-red-600 px-4 py-2 font-semibold text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-red-300"
              :disabled="!cancelForm.reason.trim()"
              @click="cancelAsCustomer"
            >
              Confirm Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
