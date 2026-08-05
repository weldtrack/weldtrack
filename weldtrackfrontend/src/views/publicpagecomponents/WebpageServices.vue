<script setup lang="ts">
import { onBeforeUnmount, onMounted, nextTick, ref, inject } from 'vue'
import type { Ref } from 'vue'
import api from '../../api/api'

interface Service {
    id: number
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
    }
}

function formatCurrency(value: number) {
    return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

onMounted(() => {
    fetchServices()
    autoplayTimer = window.setInterval(nextSlide, 5000)
})

onBeforeUnmount(() => {
    if (autoplayTimer) {
        clearInterval(autoplayTimer)
        autoplayTimer = null
    }
})
</script>

<template>
    <section id="services" class="sm:py-15">
        <div class="mx-auto max-w-7xl px-6 sm:px-12 text-center">
            <div data-reveal class="reveal mb-4 text-sm font-bold tracking-[0.3em] text-cyan-500 uppercase">Popular Services</div>
            <h2 data-reveal class="reveal mb-16 text-4xl font-extrabold tracking-tight text-white sm:text-5xl">What customers can book</h2>

            <div v-if="services.length === 0" class="mx-auto max-w-xl py-20">
                <div class="flex flex-col items-center gap-4">
                    <div class="h-10 w-10 animate-spin rounded-full border-2 border-white/5 border-t-cyan-500"></div>
                    <p class="text-slate-400">Loading available booking services...</p>
                </div>
            </div>

            <div v-else data-reveal class="reveal relative mx-auto max-w-5xl">
                <div class="group relative overflow-hidden rounded-[2.5rem] border border-white/10 bg-public-panel p-6 backdrop-blur-sm">
                    <div class="relative h-[400px] sm:h-[500px] overflow-hidden rounded-[1.5rem] shadow-2xl">
                        <transition name="fade" mode="out-in">
                            <div :key="currentSlide" class="h-full w-full">
                                <img :src="services[currentSlide]?.image_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2164&auto=format&fit=crop'"
                                    :alt="services[currentSlide]?.name"
                                    class="h-full w-full object-cover transition-transform duration-[2000ms] group-hover:scale-110" />
                                <div class="absolute inset-0 public-linear-top"></div>
                                <div class="absolute bottom-10 left-10 right-10 text-left">
                                    <div class="mb-2 inline-block rounded-full bg-cyan-500/20 px-4 py-1 text-xs font-bold tracking-widest text-cyan-400 uppercase backdrop-blur-md">
                                        {{ formatCurrency(services[currentSlide]?.price || 0) }} /hour
                                    </div>
                                    <h3 class="public-service-text mb-4 text-2xl sm:text-4xl font-black line-clamp-1 group-hover:line-clamp-none">{{ services[currentSlide]?.name }}</h3>
                                    <p class="public-service-text max-w-xl text-lg leading-relaxed line-clamp-2 group-hover:line-clamp-none">
                                        {{ services[currentSlide]?.description || 'A service option customers can book directly from the portal.' }}
                                    </p>
                                </div>
                            </div>
                        </transition>
                    </div>

                    <div class="mt-8 flex flex-col items-center justify-between gap-6 sm:flex-row">
                        <div class="flex gap-3">
                            <button @click="prevSlide" class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white transition-all hover:bg-white/10 active:scale-90">←</button>
                            <button @click="nextSlide" class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white transition-all hover:bg-white/10 active:scale-90">→</button>
                        </div>
                        <div class="flex items-center gap-2.5">
                            <button v-for="(s, i) in services" :key="s.id" @click="currentSlide = i"
                                :class="['h-1.5 rounded-full transition-all duration-500', currentSlide === i ? 'w-10 bg-cyan-400' : 'w-4 bg-white/10 hover:bg-white/20']"></button>
                        </div>
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
