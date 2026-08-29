<script setup lang="ts">
import InfoTooltip from '../../../../components/ui/InfoTooltip.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { Calendar, Clock, Check, AlertTriangle } from 'lucide-vue-next'
import { useAuthStore } from '../../../../stores/auth'
import { useAdminSectionStore } from '../../../../stores/adminSection'
import { useBookingsStore } from '../../../../stores/bookings'
import { type BookingItem } from '../../../../types/bookings'
import { useCustomerAddressesStore } from '../../../../stores/customerAddresses'
import api from '../../../../api/api'
import { getServicePriceDisplay } from '../../../../services/servicePricing'

import { useModalStore } from '../../../../stores/modal'

const auth = useAuthStore()
const adminSectionStore = useAdminSectionStore()
const bookingsStore = useBookingsStore()
const addressesStore = useCustomerAddressesStore()
const modalStore = useModalStore()

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

const services = ref<Array<{ id: string; name: string; price_hour: number }>>([])
const loadingServices = ref(false)

const selectedLaborPrice = computed(() => {
  const service = services.value.find((s) => s.name === formData.projectType)
  return service?.price_hour ?? 0
})

const selectedTotalCost = computed(() => selectedLaborPrice.value)
const activeAddress = computed(() => addressesStore.activeAddress)

const filteredBookings = computed(() => {
  const bookings = Array.isArray(bookingsStore.bookings) ? bookingsStore.bookings : []

  if (userRole.value !== 'customer') return bookings
  return bookings.filter((b) => b.email === currentEmail.value || b.customerName === currentUser.value)
})
const activeBookings = computed(() =>
  filteredBookings.value.filter((booking) => ['pending', 'confirmed', 'in-progress'].includes(booking.status.toLowerCase())),
)

const isDuplicateServiceActive = computed(() => {
  if (!formData.projectType.trim()) return false
  return activeBookings.value.some(
    (b) => b.projectType.toLowerCase().trim() === formData.projectType.toLowerCase().trim(),
  )
})

const pendingCount = computed(() => filteredBookings.value.filter((b) => b.status === 'pending').length)
const confirmedCount = computed(() => filteredBookings.value.filter((b) => b.status === 'confirmed').length)

async function fetchServices() {
  loadingServices.value = true
  try {
    const response = await api.get('/services')
    services.value = (response.data || []).map((s: any) => ({
      id: s.id,
      name: s.name,
      price_hour: s.price_hour || 0,
    }))
  } catch (error) {
    console.error('Failed to load services:', error)
    services.value = []
  } finally {
    loadingServices.value = false
  }
}

function prefillFromSelectedService() {
  const selectedService = adminSectionStore.selectedService
  if (!selectedService) return
  if (loadingServices.value || services.value.length === 0) return

  openDialogForService(selectedService.name, selectedService.description || '')
  adminSectionStore.clearSelectedService()
}

const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    await Promise.all([
      bookingsStore.fetchBookings(),
      addressesStore.fetchMyAddresses(),
      fetchServices(),
    ])

    prefillFromSelectedService()
  } finally {
    isLoading.value = false
  }
})

function resetForm() {
  formData.customerName = userRole.value === 'customer' ? currentUser.value : ''
  formData.email = userRole.value === 'customer' ? currentEmail.value : ''
  
  // Pre-fill phone if available in auth store
  formData.phone = (userRole.value === 'customer' && auth.user?.mobile_phone) ? auth.user.mobile_phone.replace('+63', '') : ''
  
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

function openDialogForService(serviceName: string, description = '') {
  if (loadingServices.value || services.value.length === 0) {
    return
  }

  resetForm()
  formData.projectType = serviceName
  formData.description = description
  isDialogOpen.value = true
}

async function handleSubmit() {
  if (userRole.value === 'customer' && !activeAddress.value) {
    return
  }
  
  if (loadingServices.value || services.value.length === 0 || !formData.projectType.trim()) {
    return
  }

  if (userRole.value === 'customer' && isDuplicateServiceActive.value) {
    modalStore.open({
      title: 'Active Booking Exists',
      message: `You already have an active booking for "${formData.projectType}". Please wait for your existing booking to be completed or cancelled before booking again.`,
      variant: 'warning',
      confirmLabel: 'Understood',
    })
    return
  }

  // Enforce validation formatting on client side execution
  const cleanPhone = formData.phone.trim().replace(/\D/g, '')
  const phPhoneRegex = /^9\d{9}$/
  
  if (!phPhoneRegex.test(cleanPhone)) {
    modalStore.open({
      title: 'Invalid Phone Number',
      message: 'Please enter a valid 10-digit Philippine phone number starting with 9 (e.g., 9123456789).',
      variant: 'error',
      confirmLabel: 'OK',
    })
    return
  }

  isSubmitting.value = true
  try {
    await bookingsStore.createBooking({
      customerName: formData.customerName,
      email: formData.email,
      phone: `+63${cleanPhone}`,
      projectType: formData.projectType,
      description: formData.description,
      status: 'pending',
      createdDate: formData.createdDate,
      preferredDate: formData.createdDate,
    })
    closeDialog()
  } catch (error: any) {
    console.error('Booking submission failed:', error)
    const backendMessage = error?.response?.data?.detail || 'Booking submission failed. Please try again.'
    modalStore.open({
      title: 'Booking Error',
      message: backendMessage,
      variant: 'error',
      confirmLabel: 'OK',
    })
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
  const service = services.value.find((s) => s.name.trim().toLowerCase() === projectType.trim().toLowerCase())
  return service?.price_hour ?? 0
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
  const labor = booking.actualLaborCost ?? getServicePriceDisplay(booking.projectType, booking.estimatedCost || getLaborCost(booking.projectType))
  return booking.totalPrice ?? labor + (booking.materialCost ?? 0)
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
  ].filter(Boolean).join(', ')
}

function getBookingTimeline(booking: BookingItem) {
  const isConfirmed = booking.status === 'confirmed' || booking.status === 'in-progress' || booking.status === 'completed'
  const isInProgress = booking.status === 'in-progress' || booking.status === 'completed'

  return [
    { label: 'Request received', time: formatCreatedDate(booking.createdDate), complete: true },
    { label: 'Schedule confirmed', time: isConfirmed && booking.scheduleDate ? formatDate(booking.scheduleDate) : 'Pending approval', complete: isConfirmed },
    { label: 'Service in progress', time: isInProgress ? 'Active' : 'Awaiting schedule', complete: isInProgress },
  ]
}
</script>

<template>
  <section class="space-y-6 relative">
    <LocalLoader v-if="isLoading" />
    <!-- List View -->
    <template v-if="!isDialogOpen && !isCancelModalOpen">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-start gap-3">
          <div class="flex h-12 w-12 items-center justify-center">
            <Calendar class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">My Bookings</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">Book welding services and track your projects</p>
          </div>
        </div>

        <button
          type="button"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs transition-colors hover:bg-sky-700 dark:bg-sky-600 dark:hover:bg-sky-500 shrink-0"
          :disabled="(userRole === 'customer' && !activeAddress) || loadingServices || services.length === 0"
          :class="(userRole === 'customer' && !activeAddress) || loadingServices || services.length === 0 ? 'cursor-not-allowed opacity-50' : ''"
          @click="openDialog"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>New Booking</span>
        </button>
      </div>

      <!-- Metric Summary Cards -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div class="rounded-xl border border-amber-200 bg-amber-50 p-5 dark:border-amber-900/50 dark:bg-amber-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300">Pending</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ pendingCount }}</p>
        </div>
        <div class="rounded-xl border border-sky-200 bg-sky-50 p-5 dark:border-sky-900/50 dark:bg-sky-950/40">
          <p class="text-xs font-bold uppercase tracking-wider text-sky-700 dark:text-sky-300">Approved</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ confirmedCount }}</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-900/60">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Total Active</p>
          <p class="mt-2 text-3xl font-black text-slate-900 dark:text-slate-100">{{ filteredBookings.length }}</p>
        </div>
      </div>

      <!-- Address Warning Banner -->
      <div v-if="userRole === 'customer' && !activeAddress" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm font-medium text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-300">
        Please add an address in the <strong class="underline font-bold">Addresses</strong> tab and set it as active before creating a new booking.
      </div>

      <!-- Full-width active bookings list -->
      <div class="grid w-full grid-cols-1 gap-4">
        <div v-if="activeBookings.length === 0" class="col-span-full rounded-2xl border border-slate-200 bg-slate-50 p-12 text-center dark:border-slate-800 dark:bg-slate-900">
          <Calendar class="mx-auto h-10 w-10 text-slate-400" />
          <h3 class="mt-3 text-lg font-bold text-slate-900 dark:text-slate-100">No active bookings yet</h3>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Your pending and ongoing project bookings will appear here.</p>
        </div>

        <article v-for="booking in activeBookings" :key="booking.id" class="min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:border-slate-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700">
          <div class="p-4 sm:p-6">
          <div>
            <div class="mb-5 flex flex-col gap-3 border-b border-slate-100 pb-5 dark:border-slate-800 sm:flex-row sm:items-start sm:justify-between">
              <div class="min-w-0 flex-1">
                <p class="break-all text-xs font-medium text-slate-400">Booking #{{ booking.id }}</p>
                <h4 class="mt-0.5 break-words text-lg font-semibold text-slate-900 dark:text-slate-100">{{ booking.projectType }}</h4>
                <p class="mt-1 break-words text-sm leading-relaxed text-slate-500 dark:text-slate-400">{{ booking.description || 'No project description provided.' }}</p>
              </div>
              <span 
                class="w-fit shrink-0 rounded-full px-3 py-1 text-xs font-semibold capitalize ring-1 ring-inset"
                :class="booking.status === 'pending'
                  ? 'bg-amber-50 text-amber-700 ring-amber-600/20 dark:bg-amber-950/60 dark:text-amber-300 dark:ring-amber-800'
                  : booking.status === 'confirmed'
                  ? 'bg-sky-50 text-sky-700 ring-sky-600/20 dark:bg-sky-950/60 dark:text-sky-300 dark:ring-sky-800'
                  : 'bg-emerald-50 text-emerald-700 ring-emerald-600/20 dark:bg-emerald-950/60 dark:text-emerald-300 dark:ring-emerald-800'"
              >
                {{ booking.status }}
              </span>
            </div>

            <!-- Details Grid with Overflow Fixes -->
            <div class="grid gap-3 text-xs sm:grid-cols-2 lg:grid-cols-3">
              <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Booking ID</p>
                <p class="mt-1 break-all font-semibold text-slate-900 dark:text-slate-100">#{{ booking.id }}</p>
              </div>

              <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Email</p>
                <p class="mt-1 break-all font-semibold text-slate-900 dark:text-slate-100">{{ booking.email }}</p>
              </div>

              <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Phone</p>
                <p class="mt-1 font-semibold text-slate-900 dark:text-slate-100 truncate">{{ booking.phone }}</p>
              </div>

              <div v-if="booking.location && (booking.location.province || booking.location.municipality || booking.location.barangay || booking.location.house)" class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Address</p>
                <p class="mt-1 break-words font-semibold leading-relaxed text-slate-900 dark:text-slate-100">{{ formatBookingAddress(booking) }}</p>
              </div>

              <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Schedule</p>
                <p class="mt-1 font-semibold text-slate-900 dark:text-slate-100 truncate">{{ getScheduleMessage(booking) }}</p>
              </div>

              <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Booked On</p>
                <p class="mt-1 font-semibold text-slate-900 dark:text-slate-100 truncate">{{ formatCreatedDate(booking.createdDate) }}</p>
              </div>

              <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Labor Cost /hr</p>
                <p class="mt-1 font-semibold text-slate-900 dark:text-slate-100 truncate">{{ formatCurrency(booking.actualLaborCost ?? getServicePriceDisplay(booking.projectType, booking.estimatedCost || getLaborCost(booking.projectType))) }}</p>
              </div>

              <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 dark:bg-slate-800/60 dark:border-slate-800 min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Material Cost</p>
                <p class="mt-1 break-words font-semibold leading-relaxed text-slate-900 dark:text-slate-100">{{ getMaterialCostMessage(booking) }}</p>
              </div>

              <!-- Total Cost Highlight -->
              <div class="col-span-full flex flex-col gap-1 rounded-xl border border-transparent bg-slate-900 p-4 text-white dark:border-slate-700 dark:bg-slate-800 sm:flex-row sm:items-center sm:justify-between">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-300">Total Project Cost</span>
                <span class="text-lg font-semibold text-white">{{ formatCurrency(getTotalCost(booking)) }}</span>
              </div>
            </div>

            <!-- Booking Timeline -->
            <div class="mt-5 rounded-xl border border-slate-100 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-800/40">
              <div class="mb-4 flex items-center justify-between">
                <span class="text-xs font-bold text-slate-900 dark:text-slate-100">Booking Progress</span>
                <span class="flex items-center gap-1.5 text-xs font-bold text-sky-600 dark:text-sky-400"><Clock class="h-3.5 w-3.5" /> Track Live</span>
              </div>
              <div class="space-y-1">
                <div v-for="(item, index) in getBookingTimeline(booking)" :key="item.label" class="relative flex gap-3 pb-4 last:pb-0">
                  <span v-if="index < 2" :class="['absolute left-[9px] top-4 h-[calc(100%-4px)] w-px', item.complete ? 'bg-sky-500' : 'bg-slate-200 dark:bg-slate-700']"></span>
                  <span :class="['relative z-10 mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full', item.complete ? 'bg-sky-600 text-white' : 'border border-sky-400 bg-sky-50 text-sky-500 dark:bg-slate-800 dark:text-sky-400']">
                    <Check v-if="item.complete" class="h-3 w-3" :stroke-width="3" />
                    <span v-else class="h-1.5 w-1.5 rounded-full bg-sky-500"></span>
                  </span>
                  <div class="flex min-w-0 flex-1 flex-col gap-0.5 sm:flex-row sm:justify-between sm:gap-3">
                    <span :class="['text-xs font-bold', item.complete ? 'text-slate-900 dark:text-slate-100' : 'text-slate-400 dark:text-slate-500']">{{ item.label }}</span>
                    <span class="text-xs text-slate-400 dark:text-slate-500 sm:shrink-0">{{ item.time }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          </div>

          <!-- Cancel Action Button -->
          <div class="flex border-t border-slate-200 bg-slate-50 px-4 py-4 dark:border-slate-800 dark:bg-slate-800/60 sm:justify-end sm:px-6" v-if="booking.status === 'pending'">
            <button
              type="button"
              class="w-full rounded-xl border border-rose-200 bg-white px-4 py-2.5 text-sm font-semibold text-rose-600 transition hover:bg-rose-100 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-400 dark:hover:bg-rose-900/60 sm:w-auto"
              @click="openCancelModal(booking)"
            >
              Cancel Booking
            </button>
          </div>
        </article>
      </div>
    </template>

    <!-- Inline Create Booking View -->
    <template v-else-if="isDialogOpen">
      <div class="rounded-2xl border border-slate-200 bg-white shadow-xs max-w-4xl mx-auto dark:border-slate-800 dark:bg-slate-900">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between dark:border-slate-800">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Create New Booking</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Please fill out your project details.</p>
          </div>
          <button 
            @click="closeDialog" 
            class="text-sm font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>
        </div>
        <div class="p-6">
          <form class="space-y-5" @submit.prevent="handleSubmit">
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="createdDate">Booked On<InfoTooltip text="Please provide the booked on date." /></label>
                <input id="createdDate" v-model="formData.createdDate" type="date" readonly class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 shadow-xs outline-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400" />
              </div>

              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="email">Email<InfoTooltip text="Please provide the email." /></label>
                <input id="email" v-model="formData.email" type="email" readonly required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 shadow-xs outline-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400" />
              </div>
            </div>

            <!-- Active Address Banner -->
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50/60 px-5 py-4 dark:border-emerald-900/50 dark:bg-emerald-950/40">
              <p class="text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300 mb-1">Active Customer Address</p>
              <p v-if="activeAddress" class="text-sm text-emerald-900 dark:text-emerald-200 font-semibold">{{ activeAddress.label }}: {{ formatActiveAddress() }}</p>
              <p v-else class="text-sm text-amber-800 dark:text-amber-300 font-medium">No active address selected. Please set one in the Addresses tab.</p>
            </div>

            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="phone">Phone Number <span class="text-rose-500">*</span><InfoTooltip text="Please provide your mobile phone number." /></label>
                <div class="flex rounded-xl border border-slate-200 bg-white shadow-xs focus-within:border-sky-500 transition dark:border-slate-800 dark:bg-slate-950">
                  <span class="inline-flex items-center px-4 bg-slate-100 text-slate-600 font-bold text-sm border-r border-slate-200 select-none dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300">
                    +63
                  </span>
                  <input 
                    id="phone" 
                    v-model="formData.phone" 
                    type="tel" 
                    required 
                    maxlength="10"
                    placeholder="9123456789"
                    pattern="9\d{9}"
                    title="Must be a 10-digit number starting with 9 (e.g., 9123456789)"
                    class="w-full bg-transparent px-4 py-3 outline-none text-slate-900 dark:text-slate-100 font-medium text-sm" 
                  />
                </div>
                <p class="mt-1.5 text-xs text-slate-400">Format: +63 followed by 10 digits (e.g., 9171234567)</p>
              </div>

              <div>
                <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="projectType">Project Type <span class="text-rose-500">*</span><InfoTooltip text="Please select the project type." /></label>
                <select id="projectType" v-model="formData.projectType" required :disabled="loadingServices || services.length === 0" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-xs disabled:opacity-50 disabled:cursor-not-allowed font-medium text-slate-800 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100 focus:border-sky-500 outline-none transition">
                  <option value="">{{ loadingServices ? 'Loading services...' : services.length === 0 ? 'No services available' : 'Select project type' }}</option>
                  <option v-for="service in services" :key="service.id" :value="service.name">{{ service.name }} — ₱{{ service.price_hour.toLocaleString() }} per hour</option>
                </select>
                <p v-if="isDuplicateServiceActive" class="mt-1.5 flex items-center gap-1.5 text-xs font-semibold text-amber-600 dark:text-amber-400">
                  <AlertTriangle class="h-4 w-4 shrink-0" />
                  <span>You already have an active booking for this service.</span>
                </p>
              </div>
            </div>

            <div class="rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-xs font-medium text-sky-800 dark:border-sky-900/50 dark:bg-sky-950/40 dark:text-sky-300 flex items-center gap-2">
              <svg class="h-4 w-4 text-sky-600 dark:text-sky-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>Material cost will be added after project completion by the team.</span>
            </div>

            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div class="rounded-xl border border-slate-200 bg-slate-50 px-5 py-3.5 shadow-xs flex justify-between items-center dark:border-slate-800 dark:bg-slate-800/60">
                <p class="text-xs font-semibold text-slate-600 dark:text-slate-400">Labor Price /hour</p>
                <p class="text-lg font-bold text-slate-900 dark:text-slate-100">{{ formatCurrency(selectedLaborPrice) }}</p>
              </div>
              <div class="rounded-xl border border-slate-800 bg-slate-900 px-5 py-3.5 shadow-xs flex justify-between items-center text-white dark:bg-slate-800 dark:border-slate-700">
                <p class="text-xs font-semibold text-slate-300">Total Estimate</p>
                <p class="text-lg font-black">{{ formatCurrency(selectedTotalCost) }}</p>
              </div>
            </div>

            <div>
              <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="description">Project Description <span class="text-rose-500">*</span><InfoTooltip text="Please provide the project description." /></label>
              <textarea id="description" v-model="formData.description" required rows="4" placeholder="Describe your welding project requirements in detail..." class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-xs focus:border-sky-500 outline-none transition dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100" />
            </div>

            <div class="flex gap-3 pt-4 border-t border-slate-100 dark:border-slate-800 justify-end">
              <button type="button" class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 disabled:opacity-50 transition-colors dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700" :disabled="isSubmitting" @click="closeDialog">Cancel</button>
              <button type="submit" class="rounded-xl bg-sky-600 px-6 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-sky-700 disabled:opacity-50 inline-flex items-center justify-center gap-2 transition-all dark:bg-sky-600 dark:hover:bg-sky-500" :disabled="isSubmitting || (userRole === 'customer' && !activeAddress) || loadingServices || services.length === 0 || !formData.projectType.trim() || isDuplicateServiceActive">
                <svg v-if="isSubmitting" class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ isSubmitting ? 'Booking...' : 'Submit Booking' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>

    <!-- Inline Cancel Booking View -->
    <template v-else-if="isCancelModalOpen">
      <div class="rounded-2xl border border-slate-200 bg-white shadow-xs max-w-2xl mx-auto dark:border-slate-800 dark:bg-slate-900">
        <div class="border-b border-slate-100 px-6 py-5 flex items-center justify-between dark:border-slate-800">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Cancel Booking</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Please tell us why you are cancelling this booking.</p>
          </div>
          <button 
            @click="closeCancelModal" 
            class="text-sm font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>
        </div>
        <div class="p-6">
          <div class="space-y-5">
            <div>
              <label class="flex items-center text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5" for="customerCancelReason">Cancellation Reason <span class="text-rose-500">*</span><InfoTooltip text="Please provide the cancel reason." /></label>
              <textarea
                id="customerCancelReason"
                v-model="cancelForm.reason"
                rows="4"
                placeholder="Tell us why you are cancelling this booking..."
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-xs focus:border-rose-500 outline-none transition dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
              />
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3">
            <button type="button" class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 transition-colors dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700" @click="closeCancelModal">Back</button>
            <button
              type="button"
              class="rounded-xl bg-rose-600 px-6 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-50 transition-all dark:bg-rose-600 dark:hover:bg-rose-500"
              :disabled="!cancelForm.reason.trim()"
              @click="cancelAsCustomer"
            >
              Confirm Cancellation
            </button>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
