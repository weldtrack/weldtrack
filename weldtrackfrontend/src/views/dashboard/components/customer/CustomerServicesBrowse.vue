<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { ArrowUpRight, Briefcase, ShieldCheck, Search, AlertCircle } from 'lucide-vue-next'
import api from '../../../../api/api'
import { useAdminSectionStore } from '../../../../stores/adminSection'
import { useBookingsStore } from '../../../../stores/bookings'
import { useAuthStore } from '../../../../stores/auth'
import { useModalStore } from '../../../../stores/modal'
import { useRouter } from 'vue-router'
import { resolveImageUrl } from '../../../../services/images'

const router = useRouter()
const adminSectionStore = useAdminSectionStore()
const bookingsStore = useBookingsStore()
const authStore = useAuthStore()
const modalStore = useModalStore()

interface Service {
  id: string
  name: string
  description: string | null
  price_hour: number
  image_url: string | null
}

const services = ref<Service[]>([])
const loading = ref(false)
const searchTerm = ref('')

async function fetchData() {
  loading.value = true
  try {
    const [serviceRes] = await Promise.all([
      api.get('/services'),
      bookingsStore.fetchBookings(),
    ])
    services.value = Array.isArray(serviceRes.data) ? serviceRes.data : []
  } catch (error) {
    console.error('Failed to load data:', error)
    services.value = []
  } finally {
    loading.value = false
  }
}

const userEmail = computed(() => authStore.user?.email || '')

const activeBookings = computed(() => {
  const all = Array.isArray(bookingsStore.bookings) ? bookingsStore.bookings : []
  return all.filter(
    (b) =>
      b.email === userEmail.value &&
      ['pending', 'confirmed', 'in-progress'].includes(b.status.toLowerCase()),
  )
})

function isAlreadyBooked(serviceName: string) {
  return activeBookings.value.some(
    (b) => b.projectType.toLowerCase().trim() === serviceName.toLowerCase().trim(),
  )
}

const filteredServices = computed(() => {
  if (!searchTerm.value.trim()) return services.value
  const term = searchTerm.value.toLowerCase().trim()
  return services.value.filter(
    (s) => s.name.toLowerCase().includes(term) || (s.description && s.description.toLowerCase().includes(term)),
  )
})

function openBooking(service: Service) {
  if (isAlreadyBooked(service.name)) {
    modalStore.open({
      title: 'Active Booking Exists',
      message: `You already have an active booking for "${service.name}". Please wait for your existing booking to be completed or cancelled before booking again.`,
      variant: 'warning',
      confirmLabel: 'Understood',
    })
    return
  }
  adminSectionStore.setSelectedService(service)
  router.push({ name: 'customer-booking' })
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <section class="relative space-y-6">
    <LocalLoader v-if="loading" />

    <!-- Header -->
    <div class="overflow-hidden rounded-3xl border border-sky-100 bg-linear-to-r from-sky-50 via-white to-cyan-50 p-6 shadow-sm dark:border-slate-800 dark:from-slate-900 dark:via-slate-900 dark:to-sky-950/40 sm:flex sm:items-center sm:justify-between">
      <div class="flex items-start gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-600 text-white shadow-lg shadow-sky-600/20">
          <Briefcase class="dashboard-view-icon h-6 w-6 text-sky-600 dark:text-sky-400" />
        </div>
        <div>
          <h3 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">Professional Services</h3>
          <p class="text-sm text-slate-600 dark:text-slate-400">Browse welding services and initiate tailored project requests</p>
        </div>
      </div>

      <div class="mt-4 flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/50 dark:text-emerald-300 sm:mt-0 shrink-0">
        <ShieldCheck class="h-4 w-4 text-emerald-500" />
        <span>Transparent Rates & Verified Quality</span>
      </div>
    </div>

    <!-- Search Input Bar -->
    <div class="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="relative">
        <Search class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search services by name or keyword..."
          class="w-full rounded-xl border border-transparent bg-slate-50 py-3 pl-10 pr-4 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-4 focus:ring-sky-500/10 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-sky-500 max-w-xl"
        />
      </div>
    </div>

    <!-- Loading & Empty States -->
    <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-12 text-center text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
      Loading available services...
    </div>

    <div v-else-if="filteredServices.length === 0" class="rounded-2xl border border-slate-200 bg-white p-12 text-center dark:border-slate-800 dark:bg-slate-900">
      <Briefcase class="mx-auto h-10 w-10 text-slate-400" />
      <h4 class="mt-3 text-base font-bold text-slate-900 dark:text-slate-100">
        {{ searchTerm ? 'No matching services found' : 'No services available' }}
      </h4>
      <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
        {{ searchTerm ? 'Try adjusting your search query.' : 'Check back later for updated service listings.' }}
      </p>
    </div>

    <!-- Full-width service list -->
    <div v-else class="grid w-full grid-cols-1 gap-4">
      <article
        v-for="service in filteredServices"
        :key="service.id"
        class="group grid min-w-0 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition duration-300 hover:-translate-y-0.5 hover:border-sky-300 hover:shadow-xl dark:border-slate-800 dark:bg-slate-900 dark:hover:border-sky-800 md:grid-cols-[18rem_minmax(0,1fr)]"
      >
        <!-- Service Image or Banner Header -->
        <div class="relative h-52 overflow-hidden bg-slate-100 dark:bg-slate-800 md:h-full md:min-h-64">
          <img
            v-if="service.image_url"
            :src="resolveImageUrl(service.image_url)"
            :alt="service.name"
            class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div v-else class="flex h-full w-full items-center justify-center bg-linear-to-br from-sky-50 to-slate-100 dark:from-slate-800 dark:to-slate-900">
            <Briefcase class="h-10 w-10 text-slate-300 dark:text-slate-700" />
          </div>
          <div class="pointer-events-none absolute inset-0 bg-linear-to-t from-slate-950/55 via-transparent to-transparent md:bg-linear-to-r"></div>
          <span class="absolute bottom-4 left-4 rounded-xl bg-white px-3 py-2 text-sm font-extrabold text-slate-950 shadow-lg dark:bg-slate-950/90 dark:text-white dark:ring-1 dark:ring-white/15 dark:backdrop-blur-sm">{{ formatCurrency(service.price_hour) }} <span class="text-xs font-medium text-slate-500 dark:text-slate-300">/ hour</span></span>
        </div>

        <!-- Card Body -->
        <div class="flex min-w-0 flex-col p-5 sm:p-7">
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="text-xs font-semibold uppercase tracking-wider text-sky-600 dark:text-sky-400">Welding Service</span>
              <span v-if="isAlreadyBooked(service.name)" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 ring-1 ring-inset ring-amber-600/20 dark:bg-amber-950/60 dark:text-amber-300 dark:ring-amber-800">
                <AlertCircle class="h-3.5 w-3.5" />
                Active booking
              </span>
            </div>
            <h4 class="mt-3 break-words text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">{{ service.name }}</h4>
            <p class="mt-3 max-w-3xl break-words text-sm leading-7 text-slate-600 dark:text-slate-400">
              {{ service.description || 'Professional welding service tailored to your exact project specifications.' }}
            </p>
          </div>

          <div class="mt-6 flex flex-col gap-3 border-t border-slate-100 pt-4 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
            <p class="text-xs font-medium text-slate-500 dark:text-slate-400">Final cost may vary based on materials and project requirements.</p>
            <button
              type="button"
              :class="[
                'inline-flex w-full items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold shadow-xs transition sm:w-auto',
                isAlreadyBooked(service.name)
                  ? 'cursor-not-allowed border border-amber-200 bg-amber-100 text-amber-800 opacity-90 dark:border-amber-900/50 dark:bg-amber-950/60 dark:text-amber-300'
                  : 'bg-sky-600 text-white shadow-lg shadow-sky-600/20 hover:bg-sky-700 active:scale-[0.98] dark:bg-sky-600 dark:hover:bg-sky-500'
              ]"
              @click="openBooking(service)"
            >
              <template v-if="isAlreadyBooked(service.name)">
                <AlertCircle class="h-4 w-4" />
                <span>Already Booked</span>
              </template>
              <template v-else>
                <span>Request Service</span>
                <ArrowUpRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </template>
            </button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
