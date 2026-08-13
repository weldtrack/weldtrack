<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ArrowUpRight, Clock3, Search, ShieldCheck, Wrench, X } from 'lucide-vue-next'
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
    <main class="mx-auto max-w-7xl px-6 pb-24 pt-28 sm:px-10 sm:pt-36">
      <section class="services-hero relative overflow-hidden rounded-3xl border px-6 py-12 text-center shadow-2xl sm:px-12 sm:py-16">
        <div class="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-sky-500/15 blur-3xl"></div>
        <div class="pointer-events-none absolute -bottom-32 -left-20 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl"></div>
        <div class="relative mx-auto max-w-3xl">
          <div class="mx-auto inline-flex items-center gap-2 rounded-full border border-sky-400/25 bg-sky-500/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.2em] text-sky-400">
            <ShieldCheck class="h-4 w-4" /> Professional welding
          </div>
          <h1 class="mt-5 text-4xl font-black tracking-tight text-[color:var(--public-text)] sm:text-6xl">Built strong. Repaired right.</h1>
          <p class="services-intro mx-auto mt-5 max-w-2xl text-base leading-7 sm:text-lg">Explore every service, compare transparent hourly labor rates, and find the right expertise for your next project.</p>
        </div>

        <div class="relative mx-auto mt-9 max-w-2xl">
          <Search class="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
        <input v-model="search" type="search" placeholder="Search by service name or description..." aria-label="Search services"
            class="w-full rounded-2xl border border-slate-300 bg-white py-4 pl-13 pr-12 text-slate-950 shadow-xl outline-none placeholder:text-slate-500 focus:border-sky-500 focus:ring-4 focus:ring-sky-500/15" />
          <button v-if="search" type="button" aria-label="Clear search" class="absolute right-4 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-900" @click="search = ''"><X class="h-4 w-4" /></button>
        </div>
      </section>

      <div v-if="!loading && !loadError" class="mt-10 flex items-center justify-between gap-4">
        <div>
          <p class="service-title text-xl font-bold">{{ search ? 'Search results' : 'Available services' }}</p>
          <p class="services-muted mt-1 text-sm">{{ filteredServices.length }} {{ filteredServices.length === 1 ? 'service' : 'services' }} available</p>
        </div>
        <div class="services-muted hidden items-center gap-2 text-sm sm:flex"><Clock3 class="h-4 w-4 text-sky-500" /> Rates shown per labor hour</div>
      </div>

      <div v-if="loading" class="services-muted py-20 text-center">Loading services...</div>
      <div v-else-if="loadError" class="mx-auto mt-12 max-w-xl rounded-xl border border-red-500/30 bg-red-950 p-6 text-center text-white">{{ loadError }}</div>
      <div v-else-if="filteredServices.length === 0" class="py-20 text-center">
        <Wrench class="mx-auto h-8 w-8 text-sky-400" />
        <p class="mt-3 font-semibold text-[color:var(--public-text)]">No matching services found.</p>
      </div>

      <div v-else class="mt-6 grid gap-7 md:grid-cols-2 lg:grid-cols-3">
        <article v-for="service in filteredServices" :id="`service-${service.id}`" :key="service.id"
          :class="['service-card group overflow-hidden rounded-3xl border shadow-lg transition duration-300 hover:-translate-y-1.5 hover:border-sky-500 hover:shadow-2xl', route.query.service === service.id ? 'border-sky-400 ring-2 ring-sky-400/40' : 'border-slate-800']">
          <div class="relative h-60 overflow-hidden">
            <img :src="getImageUrl(service.image_url)" :alt="service.name" class="h-full w-full object-cover transition duration-700 group-hover:scale-105" />
            <div class="absolute inset-0 bg-linear-to-t from-slate-950/80 via-transparent to-transparent"></div>
            <span class="service-price absolute bottom-4 left-4 inline-flex rounded-xl px-3.5 py-2 text-xs font-extrabold shadow-lg">{{ formatCurrency(service.price_hour) }} <span class="ml-1 font-medium opacity-70">/ hour</span></span>
          </div>
          <div class="flex min-h-64 flex-col p-6">
            <h2 class="service-title mt-4 text-xl font-bold">{{ service.name }}</h2>
            <p class="service-description mt-2 flex-1 text-sm leading-6">{{ service.description || 'Contact us to discuss the requirements for this service.' }}</p>
            <RouterLink to="/signup" class="service-request mt-6 inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-3 text-sm font-bold shadow-lg shadow-sky-600/15 transition hover:bg-sky-500">Request this service <ArrowUpRight class="h-4 w-4" /></RouterLink>
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
.services-hero { border-color: #1e293b; background: linear-gradient(145deg, #0f172a 0%, #020617 70%); }
.service-card { background: #020617; }
.service-price { background: #ffffff; color: #020617; }
.service-title { color: #ffffff; }
.service-description { color: #e2e8f0; }
.service-request { color: #ffffff; }

.theme-light .services-intro,
.theme-light .services-muted { color: #475569; }
.theme-light .services-hero { border-color: #e2e8f0; background: linear-gradient(145deg, #ffffff 0%, #f0f9ff 100%); }
.theme-light .service-card { background: #ffffff; }
.theme-light .service-price { background: #0f172a; color: #ffffff; }
.theme-light .service-title { color: #0f172a; }
.theme-light .service-description { color: #475569; }
.theme-light .service-request { color: #ffffff !important; }
</style>
