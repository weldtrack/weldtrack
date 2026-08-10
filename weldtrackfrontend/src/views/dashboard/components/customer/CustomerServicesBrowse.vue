<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LocalLoader from '../../../../components/ui/LocalLoader.vue'
import { Briefcase } from 'lucide-vue-next'
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
  <section class="space-y-6 relative">
    <LocalLoader v-if="loading" />
    <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-br from-cyan-50 to-white ring-1 ring-cyan-100">
          <Briefcase class="dashboard-view-icon h-6 w-6 text-cyan-600 dark:text-cyan-400" />
        </div>
        <div>
          <h3 class="text-2xl font-semibold text-gray-900">Browse Services</h3>
          <p class="mt-1 text-sm text-gray-600">Choose a service, then jump straight into the booking form.</p>
        </div>
      </div>
      <p class="text-sm text-gray-500">
        Tap a card to prefill your booking request.
      </p>
    </div>

    <div v-if="loading" class="rounded-2xl border border-gray-200 bg-white p-10 text-center text-gray-500">
      Loading available services...
    </div>

    <div v-else-if="services.length === 0" class="rounded-2xl border border-gray-200 bg-white p-10 text-center text-gray-500">
      No services are available right now.
    </div>

    <div v-else class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="service in services"
        :key="service.id"
        class="group flex flex-col overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-sm transition-all hover:shadow-lg hover:border-cyan-100"
      >
        <div class="relative h-56 overflow-hidden">
          <img
            :src="service.image_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1600&auto=format&fit=crop'"
            :alt="service.name"
            class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
          />
          <div class="absolute inset-0 bg-[linear-gradient(180deg,transparent_30%,rgba(15,23,42,0.6)_100%)]"></div>
          <div class="absolute top-4 right-4 rounded-full bg-white/20 backdrop-blur-md px-3 py-1 text-xs font-bold text-white shadow-sm border border-white/20">
            {{ formatCurrency(service.price) }}
          </div>
        </div>

        <div class="flex flex-1 flex-col p-6">
          <div class="mb-4 flex-1">
            <h4 class="text-xl font-bold text-slate-900">{{ service.name }}</h4>
            <p class="mt-2 text-sm leading-relaxed text-slate-600 line-clamp-3">
              {{ service.description || 'Professional welding service tailored to your requirements.' }}
            </p>
          </div>

          <button
            type="button"
            class="mt-auto inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition-all hover:bg-cyan-600 active:scale-95"
            @click="openBooking(service)"
          >
            Book Now
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
