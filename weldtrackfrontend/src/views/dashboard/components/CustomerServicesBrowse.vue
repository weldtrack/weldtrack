<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Briefcase } from 'lucide-vue-next'
import api from '../../../services/api'
import { useAdminSectionStore } from '../../../stores/adminSection'

interface Service {
  id: number
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
  adminSectionStore.setSection('booking')
}

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

onMounted(() => {
  fetchServices()
})
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div class="flex items-start gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-br from-cyan-50 to-white ring-1 ring-cyan-100">
          <Briefcase class="h-6 w-6 text-cyan-600" />
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

    <div v-else class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="service in services"
        :key="service.id"
        class="group overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-sm transition-all hover:-translate-y-1 hover:shadow-xl"
      >
        <div class="relative h-52 overflow-hidden bg-gray-100">
          <img
            :src="service.image_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1600&auto=format&fit=crop'"
            :alt="service.name"
            class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
          />
          <div class="absolute inset-0 bg-[linear-gradient(180deg,transparent_35%,rgba(2,6,23,0.7)_100%)]"></div>
          <div class="absolute bottom-4 left-4 rounded-full bg-white/90 px-3 py-1 text-xs font-bold text-slate-900 shadow-sm">
            {{ formatCurrency(service.price) }}
          </div>
        </div>

        <div class="space-y-4 p-5">
          <div>
            <h4 class="text-lg font-bold text-gray-900">{{ service.name }}</h4>
            <p class="mt-2 text-sm leading-relaxed text-gray-600">
              {{ service.description || 'Book this service directly from your customer dashboard.' }}
            </p>
          </div>

          <div class="flex items-center justify-between gap-3">
            <span class="text-sm font-semibold text-cyan-700">Available for booking</span>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-full bg-cyan-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700"
              @click="openBooking(service)"
            >
              Book Service
            </button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
