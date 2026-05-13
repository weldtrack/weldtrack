<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Calendar } from 'lucide-vue-next'
import { useAuthStore } from '../../../stores/auth'
import { useBookingsStore, type BookingItem } from '../../../stores/bookings'
import { useCustomerAddressesStore } from '../../../stores/customerAddresses'
import ModalShell from '../../../components/ui/ModalShell.vue'
import api from '../../../services/api'

const auth = useAuthStore()
const bookingsStore = useBookingsStore()
const addressesStore = useCustomerAddressesStore()

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

const isSubmitting = ref(false)

const services = ref<Array<{ id: number; name: string; price: number }>>([]);
const loadingServices = ref(false)

const selectedLaborPrice = computed(() => {
  const service = services.value.find((s) => s.name === formData.projectType)
  return service?.price ?? 0
})

const selectedTotalCost = computed(() => selectedLaborPrice.value)
const activeAddress = computed(() => addressesStore.activeAddress)

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

async function fetchServices() {
  loadingServices.value = true
  try {
    const response = await api.get('/services')
    services.value = (response.data || []).map((s: any) => ({
      id: s.id,
      name: s.name,
      price: s.price || 0,
    }))
  } catch (error) {
    console.error('Failed to load services:', error)
    services.value = []
  } finally {
    loadingServices.value = false
  }
}

onMounted(() => {
  bookingsStore.fetchBookings()
  addressesStore.fetchMyAddresses()
  fetchServices()
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
  if (loadingServices.value || services.value.length === 0) {
    return
  }
  resetForm()
  isDialogOpen.value = true
}

async function handleSubmit() {
  if (userRole.value === 'customer' && !activeAddress.value) {
    return
  }
  
  if (loadingServices.value || services.value.length === 0 || !formData.projectType.trim()) {
    return
  }

  isSubmitting.value = true
  try {
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
  } catch (error) {
  } finally {
    isSubmitting.value = false
  }
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

async function cancelAsCustomer() {
  if (!selectedBooking.value) return
  if (selectedBooking.value.status !== 'pending') return
  if (!cancelForm.reason.trim()) return

  await bookingsStore.updateBooking(selectedBooking.value.id, {
    status: 'cancelled',
    cancelReason: cancelForm.reason.trim(),
    cancelledBy: 'customer',
  })
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
  const service = services.value.find((s) => s.name === projectType)
  return service?.price ?? 0
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

function formatBookingAddress(booking: BookingItem) {
  const address = booking.location
  if (!address) return ''
  return [address.house, address.barangay, address.municipality, address.province].filter(Boolean).join(', ')
}

function formatActiveAddress() {
  if (!activeAddress.value) return ''
  return [
    activeAddress.value.house,
    activeAddress.value.barangay,
    activeAddress.value.municipality,
    activeAddress.value.province,
    activeAddress.value.region,
    activeAddress.value.country,
  ]
    .filter(Boolean)
    .join(', ')
}
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-blue-50 to-white ring-1 ring-blue-100">
          <Calendar class="h-6 w-6 text-blue-600" />
        </div>
        <div>
          <h3 class="mb-1 text-2xl font-semibold text-gray-900">My Bookings</h3>
          <p class="text-sm text-gray-600">Book welding services and track your projects</p>
        </div>
      </div>

      <button
        type="button"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
          :disabled="(userRole === 'customer' && !activeAddress) || loadingServices || services.length === 0"
          :class="(userRole === 'customer' && !activeAddress) || loadingServices || services.length === 0 ? 'cursor-not-allowed opacity-60' : ''"
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

    <div v-if="userRole === 'customer' && !activeAddress" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      Add an address in the `Addresses` tab and set one as active before creating a booking.
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
            <p class="mt-1 text-sm text-gray-500">Booking #{{ booking.id }}</p>
          </div>
        </div>

        <div class="grid gap-3 text-sm sm:grid-cols-2">
          <div class="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-gray-600 font-medium">Booking ID</p>
            <p class="mt-1 text-gray-900 font-medium">#{{ booking.id }}</p>
          </div>

          <div class="rounded-lg bg-blue-50 border border-blue-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-blue-600 font-medium">Email</p>
            <p class="mt-1 text-gray-900 font-medium">{{ booking.email }}</p>
          </div>

          <div class="rounded-lg bg-green-50 border border-green-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-green-600 font-medium">Phone</p>
            <p class="mt-1 text-gray-900 font-medium">{{ booking.phone }}</p>
          </div>

          <div v-if="booking.location && (booking.location.province || booking.location.municipality || booking.location.barangay || booking.location.house)" class="rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2">
            <p class="text-xs uppercase tracking-wide text-emerald-600 font-medium">Address</p>
            <p class="mt-1 text-gray-900 font-medium text-sm">{{ formatBookingAddress(booking) }}</p>
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

    <ModalShell
      :show="isDialogOpen"
      title="Create New Booking"
      subtitle="Customer request"
      tone="blue"
      size="xl"
      @close="closeDialog"
    >
      <form class="space-y-4" @submit.prevent="handleSubmit">
          <div>
            <label class="block text-sm font-medium text-gray-700" for="createdDate">Booked On</label>
            <input id="createdDate" v-model="formData.createdDate" type="date" readonly class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 shadow-sm" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700" for="email">Email</label>
            <input id="email" v-model="formData.email" type="email" readonly required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 shadow-sm" />
          </div>

          <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
            <p class="text-sm font-semibold text-emerald-900">Active Address</p>
            <p v-if="activeAddress" class="mt-1 text-sm text-emerald-800">{{ activeAddress.label }}: {{ formatActiveAddress() }}</p>
            <p v-else class="mt-1 text-sm text-amber-800">No active address selected.</p>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700" for="phone">Phone Number</label>
              <input id="phone" v-model="formData.phone" type="tel" required class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700" for="projectType">Project Type</label>
              <select id="projectType" v-model="formData.projectType" required :disabled="loadingServices || services.length === 0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
                <option value="">{{ loadingServices ? 'Loading services...' : services.length === 0 ? 'No services available' : 'Select project type' }}</option>
                <option v-for="service in services" :key="service.id" :value="service.name">{{ service.name }} — ₱{{ service.price.toLocaleString() }}</option>
              </select>
            </div>
          </div>

          <div class="rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
            Material cost will be displayed after project completion.
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
              <p class="text-sm text-gray-600">Labor Cost</p>
              <p class="mt-1 text-lg font-semibold text-gray-900">{{ formatCurrency(selectedLaborPrice) }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
              <p class="text-sm text-gray-600">Total Cost</p>
              <p class="mt-1 text-lg font-semibold text-gray-900">{{ formatCurrency(selectedTotalCost) }}</p>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700" for="description">Project Description</label>
            <textarea id="description" v-model="formData.description" required rows="4" placeholder="Describe your welding project requirements..." class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm" />
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="isSubmitting" @click="closeDialog">Cancel</button>
            <button type="submit" class="flex-1 rounded-xl bg-linear-to-r from-blue-600 to-sky-600 px-4 py-3 font-semibold text-white shadow-lg shadow-blue-600/20 hover:from-blue-700 hover:to-sky-700 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2" :disabled="isSubmitting || (userRole === 'customer' && !activeAddress) || loadingServices || services.length === 0 || !formData.projectType.trim()">
              <svg v-if="isSubmitting" class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ isSubmitting ? 'Booking...' : 'Submit Booking' }}</span>
            </button>
          </div>
      </form>
    </ModalShell>

    <ModalShell
      :show="isCancelModalOpen"
      title="Cancel Booking"
      subtitle="Tell us why you're cancelling"
      tone="red"
      size="lg"
      @close="closeCancelModal"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700" for="customerCancelReason">Cancel Reason</label>
          <textarea
            id="customerCancelReason"
            v-model="cancelForm.reason"
            rows="4"
            placeholder="Tell us why you are cancelling this booking..."
            class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm"
          />
        </div>
      </div>

      <template #footer>
        <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeCancelModal">Back</button>
        <button
          type="button"
          class="rounded-xl bg-linear-to-r from-red-600 to-rose-600 px-4 py-3 font-semibold text-white shadow-lg shadow-red-600/20 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="!cancelForm.reason.trim()"
          @click="cancelAsCustomer"
        >
          Confirm Cancel
        </button>
      </template>
    </ModalShell>
  </section>
</template>
