<script setup lang="ts">
import { onBeforeUnmount, onMounted, nextTick, ref, inject } from 'vue'
import type { Ref } from 'vue'
import api from '../../api/api'
import { ArrowLeft, ArrowRight, Wrench } from 'lucide-vue-next'

interface Service {
    id: string
    name: string
    description: string | null
    price: number
    image_url: string | null
    created_at: string
    updated_at: string
}

const observerRef = inject<Ref<IntersectionObserver | null>>('observer')

const services = ref<Service[]>([])
const currentSlide = ref(0)
const isLoading = ref(true)
const loadError = ref('')
let autoplayTimer: number | null = null

function nextSlide() {
    if (services.value.length === 0) return
    currentSlide.value = (currentSlide.value + 1) % services.value.length
}

function prevSlide() {
    if (services.value.length === 0) return
    currentSlide.value = (currentSlide.value - 1 + services.value.length) % services.value.length
}

async function fetchServices() {
    isLoading.value = true
    loadError.value = ''
    try {
        const response = await api.get('/services?limit=5')
        services.value = response.data || []
        await nextTick()
        document.querySelectorAll<HTMLElement>('[data-reveal]').forEach((el) => {
            if (!el.classList.contains('is-visible')) {
                observerRef?.value?.observe(el)
            }
        })
    } catch (err) {
        console.error('Failed to fetch services:', err)
        services.value = []
        loadError.value = 'Services are temporarily unavailable. Please try again.'
    } finally {
        isLoading.value = false
    }
}

function formatCurrency(value: number) {
    return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

function stopAutoplay() {
    if (autoplayTimer) window.clearInterval(autoplayTimer)
    autoplayTimer = null
}

function startAutoplay() {
    stopAutoplay()
    autoplayTimer = window.setInterval(nextSlide, 5000)
}

onMounted(() => {
    fetchServices()
    startAutoplay()
})

onBeforeUnmount(() => {
    if (autoplayTimer) {
        stopAutoplay()
    }
})
</script>

<template>
    <section id="services" class="relative py-16 sm:py-24 border-t border-slate-800/60">
        <div class="mx-auto max-w-7xl px-6 sm:px-10 text-center">
            <div data-reveal class="reveal mb-3 text-xs font-semibold tracking-wider text-sky-400 uppercase">Available services</div>
            <h2 data-reveal class="reveal text-3xl font-bold tracking-tight text-white sm:text-4xl">What can we help you build or repair?</h2>
            <p data-reveal class="reveal mx-auto mb-12 mt-4 max-w-2xl text-base leading-7 text-slate-300">Browse the shop’s current services and starting labor rates. Final costs depend on the job and materials required.</p>

            <div v-if="isLoading" class="mx-auto max-w-xl py-16" role="status">
                <div class="flex flex-col items-center gap-4">
                    <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-sky-500"></div>
                    <p class="text-xs text-slate-400">Loading services...</p>
                </div>
            </div>

            <div v-else-if="loadError" class="mx-auto max-w-lg rounded-xl border border-red-500/20 bg-red-500/10 p-6">
                <p class="text-sm font-semibold text-red-300">{{ loadError }}</p>
                <button type="button" class="mt-4 rounded-lg border border-slate-700 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800" @click="fetchServices">Try again</button>
            </div>

            <div v-else-if="services.length === 0" class="mx-auto max-w-lg rounded-xl border border-slate-800 bg-slate-900/60 p-8">
                <Wrench class="mx-auto h-7 w-7 text-sky-400" />
                <h3 class="mt-3 text-base font-semibold text-white">New services coming soon</h3>
                <p class="mt-1 text-xs text-slate-400">Contact us and we’ll assist with your specific welding requirements.</p>
            </div>

            <div v-else data-reveal class="reveal relative mx-auto max-w-5xl" @mouseenter="stopAutoplay" @mouseleave="startAutoplay">
                <div class="group relative overflow-hidden rounded-xl border border-slate-800 bg-slate-900/80 p-3 shadow-xl backdrop-blur-sm sm:p-4">
                    <div class="relative h-[380px] overflow-hidden rounded-lg sm:h-[460px]">
                        <transition name="fade" mode="out-in">
                            <div :key="currentSlide" class="h-full w-full">
                                <img :src="services[currentSlide]?.image_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2164&auto=format&fit=crop'"
                                    :alt="services[currentSlide]?.name"
                                    class="h-full w-full object-cover transition-transform duration-[2000ms] group-hover:scale-105" />
                                <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
                                <div class="absolute inset-x-5 bottom-5 text-left sm:inset-x-8 sm:bottom-8">
                                    <div class="mb-2.5 inline-block rounded-md border border-slate-700 bg-slate-900/80 px-3 py-1 text-xs font-semibold text-sky-400 backdrop-blur-md">
                                        Starting at {{ formatCurrency(services[currentSlide]?.price || 0) }}
                                    </div>
                                    <h3 class="public-service-text mb-2 text-2xl font-bold text-white sm:text-4xl">{{ services[currentSlide]?.name }}</h3>
                                    <p class="public-service-text max-w-xl text-sm leading-6 text-slate-300">
                                        {{ services[currentSlide]?.description || 'A service option customers can book directly from the portal.' }}
                                    </p>
                                </div>
                            </div>
                        </transition>
                    </div>

                    <div class="flex flex-col items-center justify-between gap-4 px-2 pb-1 pt-4 sm:flex-row">
                        <div class="flex gap-2">
                            <button type="button" aria-label="Previous service" @click="prevSlide" class="flex h-9 w-9 items-center justify-center rounded-md border border-slate-800 bg-slate-800/60 text-slate-300 transition-all hover:bg-slate-800 hover:text-white active:scale-95"><ArrowLeft class="h-4 w-4" /></button>
                            <button type="button" aria-label="Next service" @click="nextSlide" class="flex h-9 w-9 items-center justify-center rounded-md border border-slate-800 bg-slate-800/60 text-slate-300 transition-all hover:bg-slate-800 hover:text-white active:scale-95"><ArrowRight class="h-4 w-4" /></button>
                        </div>
                        <div class="flex items-center gap-2">
                            <button v-for="(s, i) in services" :key="s.id" type="button" :aria-label="`View ${s.name}`" @click="currentSlide = i"
                                :class="['h-1.5 rounded-full transition-all duration-300', currentSlide === i ? 'w-6 bg-sky-500' : 'w-3 bg-slate-700 hover:bg-slate-600']"></button>
                        </div>
                        <RouterLink to="/signup" class="group inline-flex items-center gap-2 rounded-lg bg-sky-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-sky-500">Request this service <ArrowRight class="h-3.5 w-3.5 transition group-hover:translate-x-0.5" /></RouterLink>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
<style scoped>
.public-service-text {
    color: var(--public-service-text, rgba(227, 227, 227, 0.95));}
</style>
