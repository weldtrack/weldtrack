<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { Search, Wrench } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import api from '../api/api'
import { useThemeMode } from '../composables/useThemeMode'
import WebpageNavbar from './publicpagecomponents/WebpageNavbar.vue'
import WebpageFooter from './publicpagecomponents/WebpageFooter.vue'
import { resolveImageUrl } from '../services/images'

interface Service {
  id: string
  name: string
  description: string | null
  price_hour: number
  image_url: string | null
}

const route = useRoute()
const { isDarkMode } = useThemeMode()
const services = ref<Service[]>([])
const search = ref('')
const loading = ref(true)
const loadError = ref('')

const filteredServices = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return services.value
  return services.value.filter((service) =>
    service.name.toLowerCase().includes(query)
    || (service.description?.toLowerCase().includes(query) ?? false),
  )
})

function getImageUrl(url: string | null) {
  return resolveImageUrl(url) || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1600&auto=format&fit=crop'
}

function formatCurrency(value: number) {
  return `₱${Number(value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

async function fetchServices() {
  loading.value = true
  loadError.value = ''
  try {
    const response = await api.get('/services?limit=100')
    services.value = Array.isArray(response.data) ? response.data : []
    await nextTick()
    const selectedId = String(route.query.service || '')
    if (selectedId) document.getElementById(`service-${selectedId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  } catch {
    loadError.value = 'Services are temporarily unavailable. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchServices)
</script>

<template>
  <div :class="['public-theme-page min-h-screen bg-public-dark', isDarkMode ? 'theme-dark' : 'theme-light']">
    <WebpageNavbar />
    <main class="mx-auto max-w-7xl px-6 pb-20 pt-28 sm:px-10 sm:pt-36">
      <div class="mx-auto max-w-3xl text-center">
        <p class="text-xs font-bold uppercase tracking-[0.2em] text-sky-400">Our services</p>
        <h1 class="mt-3 text-4xl font-bold text-[color:var(--public-text)] sm:text-5xl">Find the right welding service</h1>
        <p class="services-intro mt-4 text-base">Search all available services and compare hourly labor prices.</p>
      </div>

      <div class="relative mx-auto mt-10 max-w-2xl">
        <Search class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
        <input v-model="search" type="search" placeholder="Search by service name or description..." aria-label="Search services"
          class="w-full rounded-xl border border-slate-700 bg-white py-4 pl-12 pr-4 text-slate-950 shadow-lg outline-none placeholder:text-slate-500 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30" />
      </div>

      <div v-if="loading" class="services-muted py-20 text-center">Loading services...</div>
      <div v-else-if="loadError" class="mx-auto mt-12 max-w-xl rounded-xl border border-red-500/30 bg-red-950 p-6 text-center text-white">{{ loadError }}</div>
      <div v-else-if="filteredServices.length === 0" class="py-20 text-center">
        <Wrench class="mx-auto h-8 w-8 text-sky-400" />
        <p class="mt-3 font-semibold text-[color:var(--public-text)]">No matching services found.</p>
      </div>

      <div v-else class="mt-12 grid gap-7 md:grid-cols-2 lg:grid-cols-3">
        <article v-for="service in filteredServices" :id="`service-${service.id}`" :key="service.id"
          :class="['service-card overflow-hidden rounded-2xl border shadow-xl transition hover:-translate-y-1 hover:border-sky-500', route.query.service === service.id ? 'border-sky-400 ring-2 ring-sky-400/40' : 'border-slate-800']">
          <img :src="getImageUrl(service.image_url)" :alt="service.name" class="h-56 w-full object-cover" />
          <div class="p-6">
            <span class="service-price inline-flex rounded-md px-3 py-1.5 text-xs font-extrabold">{{ formatCurrency(service.price_hour) }} per hour</span>
            <h2 class="service-title mt-4 text-xl font-bold">{{ service.name }}</h2>
            <p class="service-description mt-2 min-h-16 text-sm leading-6">{{ service.description || 'Contact us to discuss the requirements for this service.' }}</p>
            <RouterLink to="/signup" class="service-request mt-5 inline-flex rounded-lg bg-sky-600 px-4 py-2.5 text-sm font-bold hover:bg-sky-500">Request this service</RouterLink>
          </div>
        </article>
      </div>
    </main>
    <WebpageFooter />
  </div>
</template>

<style scoped>
.services-intro,
.services-muted { color: #94a3b8; }
.service-card { background: #020617; }
.service-price { background: #ffffff; color: #020617; }
.service-title { color: #ffffff; }
.service-description { color: #e2e8f0; }
.service-request { color: #ffffff; }

.theme-light .services-intro,
.theme-light .services-muted { color: #475569; }
.theme-light .service-card { background: #ffffff; }
.theme-light .service-price { background: #0f172a; color: #ffffff; }
.theme-light .service-title { color: #0f172a; }
.theme-light .service-description { color: #475569; }
.theme-light .service-request { color: #ffffff !important; }
</style>
