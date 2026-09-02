<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ArrowUpRight, Clock3, Search, ShieldCheck, Wrench, X } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import api from '../api/api'
import { useThemeMode } from '../composables/useThemeMode'
import WebpageNavbar from './publicpagecomponents/WebpageNavbar.vue'
import WebpageFooter from './publicpagecomponents/WebpageFooter.vue'
import { resolveImageUrl } from '../services/images'
import { formatServicePricing, formatCurrency, getPricingTypeLabel } from '../services/servicePricing'

interface Service {
  id: string
  name: string
  description: string | null
  pricing_type?: 'hourly' | 'fixed' | 'hybrid'
  price_fixed?: number
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
  const list = [...services.value].sort((a, b) => a.name.localeCompare(b.name))
  const query = search.value.trim().toLowerCase()
  if (!query) return list
  return list.filter((service) =>
    service.name.toLowerCase().includes(query)
    || (service.description?.toLowerCase().includes(query) ?? false),
  )
})

function getImageUrl(url: string | null) {
  return resolveImageUrl(url) || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1600&auto=format&fit=crop'
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
          <p class="services-intro mx-auto mt-5 max-w-2xl text-base leading-7 sm:text-lg">Explore every service, compare transparent fixed prices and hourly labor rates, and find the right expertise for your next project.</p>
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
        <div class="services-muted hidden items-center gap-2 text-sm sm:flex"><Clock3 class="h-4 w-4 text-sky-500" /> Transparent Fixed & Hourly Rates</div>
      </div>

      <div v-if="loading" class="services-muted py-20 text-center">Loading services...</div>
      <div v-else-if="loadError" class="mx-auto mt-12 max-w-xl rounded-xl border border-red-500/30 bg-red-950 p-6 text-center text-white">{{ loadError }}</div>
      <div v-else-if="filteredServices.length === 0" class="py-20 text-center">
        <Wrench class="mx-auto h-8 w-8 text-sky-400" />
        <p class="mt-3 font-semibold text-[color:var(--public-text)]">No matching services found.</p>
      </div>

      <div v-else class="mt-10 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        <article v-for="service in filteredServices" :id="`service-${service.id}`" :key="service.id"
          :class="['service-card group relative flex flex-col overflow-hidden rounded-[2rem] border transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_20px_40px_-15px_rgba(14,165,233,0.15)]', route.query.service === service.id ? 'border-sky-400 ring-4 ring-sky-400/20' : 'border-slate-800 hover:border-sky-500/50']">
          
          <div class="relative h-64 overflow-hidden bg-slate-900">
            <img :src="getImageUrl(service.image_url)" :alt="service.name" class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110" />
            <div class="absolute inset-0 bg-linear-to-t from-slate-950/90 via-slate-950/20 to-transparent transition-opacity duration-500 group-hover:opacity-80"></div>
            
            <div class="absolute right-4 top-4 rounded-full bg-slate-950/60 px-3 py-1.5 text-xs font-bold text-white backdrop-blur-md ring-1 ring-white/20">
              <div class="flex items-center gap-1.5"><ShieldCheck class="h-3.5 w-3.5 text-sky-400" /> Premium</div>
            </div>

            <div class="absolute bottom-4 left-4 right-4 flex items-end justify-between gap-2">
              <span class="service-price inline-flex items-baseline gap-1 rounded-2xl px-4 py-2 text-sm font-black shadow-2xl backdrop-blur-md">
                {{ formatServicePricing(service) }}
              </span>
              <span class="rounded-xl bg-slate-950/75 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-wider text-sky-400 backdrop-blur-md ring-1 ring-white/20">
                {{ getPricingTypeLabel(service.pricing_type) }}
              </span>
            </div>
          </div>
          
          <div class="relative flex flex-1 flex-col p-6 sm:p-8">
            <div class="mb-4 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-500">
              <Wrench class="h-4 w-4" /> Expert Service
            </div>
            <h2 class="service-title text-2xl font-black tracking-tight transition-colors group-hover:text-sky-400">{{ service.name }}</h2>
            <p class="service-description mt-3 flex-1 text-sm leading-relaxed">{{ service.description || 'Professional welding service tailored to your exact project specifications.' }}</p>

            <!-- Pricing Breakdown Details -->
            <div class="service-breakdown mt-6 rounded-2xl border border-slate-800/80 bg-slate-900/50 p-3.5">
              <div class="mb-2 flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <span>Service Pricing</span>
                <span class="rounded-md bg-sky-950/80 px-2 py-0.5 text-[10px] font-bold text-sky-300">
                  {{ getPricingTypeLabel(service.pricing_type) }}
                </span>
              </div>
              <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/60">
                <div class="flex flex-col">
                  <span class="service-breakdown-label text-[11px] font-semibold text-slate-400">Fixed / Base Price</span>
                  <span class="service-breakdown-value mt-0.5 text-sm font-black text-white">
                    {{ service.pricing_type === 'hourly' ? 'None' : formatCurrency(service.price_fixed || 0) }}
                  </span>
                </div>
                <div class="flex flex-col border-l border-slate-800/60 pl-3">
                  <span class="service-breakdown-label text-[11px] font-semibold text-slate-400">Hourly Labor</span>
                  <span class="service-breakdown-value mt-0.5 text-sm font-black text-white">
                    {{ service.pricing_type === 'fixed' ? 'None' : `${formatCurrency(service.price_hour || 0)} / hr` }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="mt-8 border-t border-slate-800/50 pt-6">
              <RouterLink to="/signup" class="service-request relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-2xl bg-sky-600 px-6 py-3.5 text-sm font-bold shadow-lg shadow-sky-600/20 transition-all hover:bg-sky-500 hover:shadow-sky-500/30 active:scale-[0.98]">
                <span class="relative z-10 flex items-center gap-2">Request this service <ArrowUpRight class="h-4.5 w-4.5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" /></span>
              </RouterLink>
            </div>
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
.theme-light .service-breakdown { border-color: #e2e8f0; background: #f8fafc; }
.theme-light .service-breakdown-label { color: #64748b; }
.theme-light .service-breakdown-value { color: #0f172a; }
</style>
