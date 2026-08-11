<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { ArrowUpRight, Briefcase, ShieldCheck } from 'lucide-vue-next'
import api from '../../../../api/api'
import { useAdminSectionStore } from '../../../../stores/adminSection'
import { useRouter } from 'vue-router'

const router = useRouter()

interface Service {
  id: string
  name: string
  description: string | null
  price: number
  image_url: string | null
}

const adminSectionStore = useAdminSectionStore()
const services = ref<Service[]>([])
const loading = ref(false)

async function fetchServices() {
  loading.value = true
  try {
    const response = await api.get('/services')
    services.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Failed to load services:', error)
    services.value = []
  } finally {
    loading.value = false
  }
}

function openBooking(service: Service) {
  adminSectionStore.setSelectedService(service)
  router.push({ name: 'customer-booking' })
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

onMounted(() => {
  fetchServices()
})
</script>

<template>
  <section class="relative space-y-7">
    <LocalLoader v-if="loading" />
    <div class="flex flex-col gap-4 border-b border-slate-200 pb-6 dark:border-slate-800 lg:flex-row lg:items-end lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800">
          <Briefcase class="dashboard-view-icon h-6 w-6 text-cyan-600 dark:text-cyan-400" />
        </div>
        <div>
          <h3 class="text-2xl font-semibold tracking-tight text-gray-900 dark:text-slate-100">Professional welding services</h3>
          <p class="mt-1 text-sm text-gray-600 dark:text-slate-400">Select a service to start a tailored project request.</p>
        </div>
      </div>
      <p class="inline-flex items-center gap-2 text-sm text-gray-500 dark:text-slate-400">
        <ShieldCheck class="h-4 w-4 text-emerald-500" />
        Transparent starting rates
      </p>
    </div>

    <div v-if="loading" class="rounded-2xl border border-gray-200 bg-white p-10 text-center text-gray-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
      Loading available services...
    </div>

    <div v-else-if="services.length === 0" class="rounded-2xl border border-dashed border-gray-200 bg-white p-10 text-center text-gray-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
      No services are available right now.
    </div>

    <div v-else class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="service in services"
        :key="service.id"
        class="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700"
      >
        <div v-if="service.image_url" class="relative h-44 overflow-hidden bg-slate-100 dark:bg-slate-800">
          <img
            :src="service.image_url"
            :alt="service.name"
            class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
          />
          <div class="absolute inset-0 bg-linear-to-t from-slate-950/35 to-transparent"></div>
        </div>

        <div class="flex flex-1 flex-col p-5 sm:p-6">
          <div class="mb-5 flex-1">
            <div class="mb-4 flex items-center justify-between gap-3">
              <span class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 dark:text-slate-500">Welding service</span>
              <span class="rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200">From {{ formatCurrency(service.price) }}</span>
            </div>
            <h4 class="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-100">{{ service.name }}</h4>
            <p class="mt-2 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-400">
              {{ service.description || 'Professional welding service tailored to your requirements.' }}
            </p>
          </div>

          <button
            type="button"
            class="mt-auto inline-flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-800 transition hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700 active:scale-[0.99] dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:border-sky-800 dark:hover:bg-sky-950/40 dark:hover:text-sky-300"
            @click="openBooking(service)"
          >
            Request this service
            <ArrowUpRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
