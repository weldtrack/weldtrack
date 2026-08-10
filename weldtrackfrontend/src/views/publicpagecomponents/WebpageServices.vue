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
    <section id="services" class="relative py-24 sm:py-32">
        <div class="mx-auto max-w-7xl px-6 sm:px-12 text-center">
            <div data-reveal class="reveal mb-4 text-sm font-bold tracking-[0.3em] text-cyan-500 uppercase">Popular Services</div>
            <h2 data-reveal class="reveal text-4xl font-black tracking-[-0.035em] text-white sm:text-5xl">Built for the work you need.</h2>
            <p data-reveal class="reveal mx-auto mb-14 mt-5 max-w-2xl text-lg leading-8 text-slate-400">Explore available services, then create an account to send your requirements and preferred schedule.</p>

            <div v-if="isLoading" class="mx-auto max-w-xl py-20" role="status">
                <div class="flex flex-col items-center gap-4">
                    <div class="h-10 w-10 animate-spin rounded-full border-2 border-white/5 border-t-cyan-500"></div>
                    <p class="text-slate-400">Loading available booking services...</p>
                </div>
            </div>

            <div v-else-if="loadError" class="mx-auto max-w-lg rounded-2xl border border-red-400/15 bg-red-400/5 p-8">
                <p class="font-semibold text-red-300">{{ loadError }}</p>
                <button type="button" class="mt-5 rounded-full border border-white/10 px-5 py-2.5 font-semibold text-white hover:bg-white/5" @click="fetchServices">Try again</button>
            </div>

            <div v-else-if="services.length === 0" class="mx-auto max-w-lg rounded-2xl border border-white/10 bg-white/[0.03] p-10">
                <Wrench class="mx-auto h-8 w-8 text-cyan-400" />
                <h3 class="mt-4 text-lg font-bold text-white">New services are coming soon</h3>
                <p class="mt-2 text-slate-400">Contact us and we’ll help with your welding requirements.</p>
            </div>

            <div v-else data-reveal class="reveal relative mx-auto max-w-6xl" @mouseenter="stopAutoplay" @mouseleave="startAutoplay">
                <div class="group relative overflow-hidden rounded-[2rem] border border-white/10 bg-public-panel p-3 shadow-2xl backdrop-blur-sm sm:p-5">
                    <div class="relative h-[430px] overflow-hidden rounded-[1.4rem] sm:h-[540px]">
                        <transition name="fade" mode="out-in">
                            <div :key="currentSlide" class="h-full w-full">
                                <img :src="services[currentSlide]?.image_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2164&auto=format&fit=crop'"
                                    :alt="services[currentSlide]?.name"
                                    class="h-full w-full object-cover transition-transform duration-[2000ms] group-hover:scale-110" />
                                <div class="absolute inset-0 public-linear-top"></div>
                                <div class="absolute inset-x-5 bottom-5 text-left sm:inset-x-10 sm:bottom-10">
                                    <div class="mb-3 inline-block rounded-full border border-cyan-300/20 bg-slate-950/45 px-4 py-1.5 text-xs font-bold tracking-widest text-cyan-300 uppercase backdrop-blur-md">
                                        Starting at {{ formatCurrency(services[currentSlide]?.price || 0) }}
                                    </div>
                                    <h3 class="public-service-text mb-3 text-3xl font-black sm:text-5xl">{{ services[currentSlide]?.name }}</h3>
                                    <p class="public-service-text max-w-2xl text-base leading-7 sm:text-lg">
                                        {{ services[currentSlide]?.description || 'A service option customers can book directly from the portal.' }}
                                    </p>
                                </div>
                            </div>
                        </transition>
                    </div>

                    <div class="flex flex-col items-center justify-between gap-5 px-2 pb-2 pt-6 sm:flex-row">
                        <div class="flex gap-3">
                            <button type="button" aria-label="Previous service" @click="prevSlide" class="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white transition-all hover:bg-white/10 active:scale-90"><ArrowLeft class="h-4 w-4" /></button>
                            <button type="button" aria-label="Next service" @click="nextSlide" class="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white transition-all hover:bg-white/10 active:scale-90"><ArrowRight class="h-4 w-4" /></button>
                        </div>
                        <div class="flex items-center gap-2.5">
                            <button v-for="(s, i) in services" :key="s.id" type="button" :aria-label="`View ${s.name}`" @click="currentSlide = i"
                                :class="['h-1.5 rounded-full transition-all duration-500', currentSlide === i ? 'w-10 bg-cyan-400' : 'w-4 bg-white/10 hover:bg-white/20']"></button>
                        </div>
                        <RouterLink to="/signup" class="group inline-flex items-center gap-2 rounded-full bg-cyan-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-cyan-300">Request this service <ArrowRight class="h-4 w-4 transition group-hover:translate-x-1" /></RouterLink>
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
