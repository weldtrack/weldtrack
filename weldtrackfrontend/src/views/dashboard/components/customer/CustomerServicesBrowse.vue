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
import { formatServicePricing, formatCurrency, getPricingTypeLabel } from '../../../../services/servicePricing'

const router = useRouter()
const adminSectionStore = useAdminSectionStore()
const bookingsStore = useBookingsStore()
const authStore = useAuthStore()
const modalStore = useModalStore()

interface Service {
  id: string
  name: string
  description: string | null
  pricing_type?: 'hourly' | 'fixed' | 'hybrid'
  price_fixed?: number
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
  const list = [...services.value].sort((a, b) => a.name.localeCompare(b.name))
  if (!searchTerm.value.trim()) return list
  const term = searchTerm.value.toLowerCase().trim()
  return list.filter(
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

    <!-- Service list -->
    <div v-else class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="service in filteredServices"
        :key="service.id"
        class="group relative flex flex-col overflow-hidden rounded-[2rem] border border-slate-200 bg-white transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_20px_40px_-15px_rgba(14,165,233,0.15)] dark:border-slate-800 dark:bg-slate-900 dark:hover:border-sky-800"
      >
        <!-- Service Image -->
        <div class="relative h-64 overflow-hidden bg-slate-100 dark:bg-slate-950">
          <img
            v-if="service.image_url"
            :src="resolveImageUrl(service.image_url)"
            :alt="service.name"
            class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
          />
          <div v-else class="flex h-full w-full items-center justify-center bg-linear-to-br from-sky-50 to-slate-200 dark:from-slate-800 dark:to-slate-900">
            <Briefcase class="h-12 w-12 text-slate-300 dark:text-slate-700" />
          </div>
          <div class="pointer-events-none absolute inset-0 bg-linear-to-t from-slate-900/80 via-slate-900/20 to-transparent transition-opacity duration-500 group-hover:opacity-90 dark:from-slate-950/90 dark:via-slate-950/40"></div>
          
          <div class="absolute right-4 top-4 rounded-full bg-slate-900/60 px-3 py-1.5 text-xs font-bold text-white backdrop-blur-md ring-1 ring-white/20 dark:bg-slate-950/60">
            <div class="flex items-center gap-1.5"><ShieldCheck class="h-3.5 w-3.5 text-sky-400" /> Premium</div>
          </div>

          <div class="absolute bottom-4 left-4 right-4 flex items-end justify-between gap-2">
            <span class="inline-flex items-baseline gap-1 rounded-2xl bg-white px-4 py-2 text-sm font-black text-slate-900 shadow-2xl dark:bg-slate-900/90 dark:text-white dark:ring-1 dark:ring-white/10 dark:backdrop-blur-md">
              {{ formatServicePricing(service) }}
            </span>
            <span class="rounded-xl bg-slate-950/75 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-wider text-sky-400 backdrop-blur-md ring-1 ring-white/20">
              {{ getPricingTypeLabel(service.pricing_type) }}
            </span>
          </div>
        </div>

        <!-- Card Body -->
        <div class="relative flex flex-1 flex-col p-6 sm:p-8">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
            <div class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-600 dark:text-sky-500">
              <Briefcase class="h-4 w-4" /> Expert Service
            </div>
            <span v-if="isAlreadyBooked(service.name)" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-amber-700 ring-1 ring-inset ring-amber-600/20 dark:bg-amber-950/60 dark:text-amber-400 dark:ring-amber-800">
              <AlertCircle class="h-3.5 w-3.5" /> Active Booking
            </span>
          </div>
          
          <h4 class="mt-1 break-words text-2xl font-black tracking-tight text-slate-900 transition-colors group-hover:text-sky-600 dark:text-slate-100 dark:group-hover:text-sky-400">{{ service.name }}</h4>
          <p class="mt-3 flex-1 break-words text-sm leading-relaxed text-slate-600 dark:text-slate-400">
            {{ service.description || 'Professional welding service tailored to your exact project specifications.' }}
          </p>

          <!-- Pricing Breakdown Details -->
          <div class="mt-6 rounded-2xl border border-slate-100 bg-slate-50/80 p-3.5 dark:border-slate-800/80 dark:bg-slate-950/50">
            <div class="mb-2 flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              <span>Service Pricing</span>
              <span class="rounded-md bg-sky-50 px-2 py-0.5 text-[10px] font-bold text-sky-700 dark:bg-sky-950/80 dark:text-sky-300">
                {{ getPricingTypeLabel(service.pricing_type) }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-200/60 dark:border-slate-800/60">
              <div class="flex flex-col">
                <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Fixed / Base Price</span>
                <span class="mt-0.5 text-sm font-black text-slate-900 dark:text-slate-100">
                  {{ service.pricing_type === 'hourly' ? 'None' : formatCurrency(service.price_fixed || 0) }}
                </span>
              </div>
              <div class="flex flex-col border-l border-slate-200/60 pl-3 dark:border-slate-800/60">
                <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Hourly Labor</span>
                <span class="mt-0.5 text-sm font-black text-slate-900 dark:text-slate-100">
                  {{ service.pricing_type === 'fixed' ? 'None' : `${formatCurrency(service.price_hour || 0)} / hr` }}
                </span>
              </div>
            </div>
          </div>

          <div class="mt-8 border-t border-slate-100 pt-6 dark:border-slate-800/60">
            <button
              type="button"
              :class="[
                'relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-2xl px-6 py-3.5 text-sm font-bold shadow-lg transition-all active:scale-[0.98]',
                isAlreadyBooked(service.name)
                  ? 'cursor-not-allowed border border-amber-200 bg-amber-50 text-amber-800 opacity-90 shadow-none dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-300'
                  : 'bg-sky-600 text-white shadow-sky-600/20 hover:bg-sky-500 hover:shadow-sky-500/30'
              ]"
              @click="openBooking(service)"
            >
              <template v-if="isAlreadyBooked(service.name)">
                <AlertCircle class="h-4.5 w-4.5" />
                <span>Already Booked</span>
              </template>
              <template v-else>
                <span class="relative z-10 flex items-center gap-2">Request Service <ArrowUpRight class="h-4.5 w-4.5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" /></span>
              </template>
            </button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
