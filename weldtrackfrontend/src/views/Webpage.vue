<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import api from '../services/api'

interface Service {
  id: number
  name: string
  description: string | null
  price: number
  image_url: string | null
  created_at: string
  updated_at: string
}

const features = [
    {
        icon: '📦',
        accent: 'bg-yellow-400',
        title: 'Inventory Management',
        description: 'Track materials, monitor stock levels, and manage low-stock alerts',
    },
    {
        icon: '🛠️',
        accent: 'bg-green-400',
        title: 'Project Tracking',
        description: 'Manage projects from conception to completion with detailed timelines',
    },
    {
        icon: '📊',
        accent: 'bg-red-400',
        title: 'Sales Tracking',
        description: 'Record transactions and generate detailed business reports',
    },
]

const highlights = [
    {
        icon: '🎯',
        title: 'Role-Based Access',
        description: 'Different interfaces for admins, staff, and customers',
    },
    {
        icon: '⚡',
        title: 'Real-Time Updates',
        description: 'Instant notifications and live data synchronization across all users',
    },
    {
        icon: '🔒',
        title: 'Secure & Reliable',
        description: 'Enterprise-grade security with role-based permissions and data protection',
    },
]

const heroStats = [
    { value: '24/7', label: 'Operational Visibility' },
    { value: '3 Roles', label: 'Tailored Access' },
    { value: '1 Platform', label: 'All Core Workflows' },
]

let observer: IntersectionObserver | null = null
const isMobileMenuOpen = ref(false)

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
    const response = await api.get('/services')
    services.value = response.data || []
    if (services.value.length === 0) {
      currentSlide.value = 0
    }
  } catch (err) {
    console.error('Failed to fetch services:', err)
    services.value = []
  }
}

onMounted(() => {
  fetchServices()
  autoplayTimer = window.setInterval(nextSlide, 4000)
})

onBeforeUnmount(() => {
  if (autoplayTimer) {
    clearInterval(autoplayTimer)
    autoplayTimer = null
  }
})

onMounted(() => {
  const targets = document.querySelectorAll<HTMLElement>('[data-reveal]')
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer?.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.2, rootMargin: '0px 0px -40px 0px' },
  )

  targets.forEach((el) => observer?.observe(el))
})

function formatCurrency(value: number) {
  return `₱${value.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}


onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
})
</script>

<template>
    <div class="relative min-h-screen overflow-hidden bg-slate-950 text-white">
        <div class="pointer-events-none absolute inset-0">
            <div class="absolute -left-24 top-20 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl"></div>
            <div class="absolute right-0 top-32 h-96 w-96 rounded-full bg-blue-500/20 blur-3xl"></div>
            <div class="absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl"></div>
        </div>

        <nav class="sticky top-0 z-20 border-b border-white/10 bg-slate-950/70 px-6 py-4 backdrop-blur-xl sm:px-8">
            <div class="mx-auto flex max-w-7xl items-center justify-between gap-4">
                <div class="flex items-center gap-3 text-2xl font-extrabold tracking-tight">
                    <span class="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10 text-lg shadow-lg shadow-cyan-950/40">⚙️</span>
                    <span>WeldTrack</span>
                </div>

                <button
                    type="button"
                    class="inline-flex items-center justify-center rounded-lg border border-white/30 p-2 text-white sm:hidden"
                    @click="isMobileMenuOpen = !isMobileMenuOpen"
                >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                </button>

                <div class="hidden flex-wrap items-center gap-6 sm:flex">
                    <a href="#home" class="text-sm font-semibold text-slate-300 transition-colors hover:text-white">Home</a>
                    <a href="#about" class="text-sm font-semibold text-slate-300 transition-colors hover:text-white">About</a>
                    <a href="#services" class="text-sm font-semibold text-slate-300 transition-colors hover:text-white">Services</a>
                    <a href="#contact" class="text-sm font-semibold text-slate-300 transition-colors hover:text-white">Contact</a>
                </div>

                <div class="hidden items-center gap-3 sm:flex">
                    <RouterLink
                        to="/signup"
                        class="flex-1 rounded-lg border border-white/15 bg-white/5 px-5 py-2 text-center font-semibold text-white transition-all hover:bg-white/10 hover:shadow-lg hover:shadow-cyan-950/20 sm:flex-none"
                    >
                        Sign Up
                    </RouterLink>

                    <RouterLink
                        to="/login"
                        class="flex-1 rounded-lg bg-linear-to-r from-cyan-400 to-white px-6 py-2 text-center font-semibold text-slate-950 transition-all hover:shadow-lg hover:shadow-cyan-950/20 sm:flex-none"
                    >
                        Sign In
                    </RouterLink>
                </div>
            </div>

            <div v-if="isMobileMenuOpen" class="mx-auto mt-4 max-w-7xl space-y-3 sm:hidden">
                <a href="#home" class="block rounded-lg border border-white/10 bg-white/5 px-4 py-2 font-semibold text-slate-200" @click="isMobileMenuOpen = false">Home</a>
                <a href="#about" class="block rounded-lg border border-white/10 bg-white/5 px-4 py-2 font-semibold text-slate-200" @click="isMobileMenuOpen = false">About</a>
                <a href="#services" class="block rounded-lg border border-white/10 bg-white/5 px-4 py-2 font-semibold text-slate-200" @click="isMobileMenuOpen = false">Services</a>
                <a href="#contact" class="block rounded-lg border border-white/10 bg-white/5 px-4 py-2 font-semibold text-slate-200" @click="isMobileMenuOpen = false">Contact</a>
                <div class="grid grid-cols-2 gap-3 pt-1">
                    <RouterLink
                        to="/signup"
                        class="rounded-lg border border-white/15 bg-white/5 px-4 py-2 text-center font-semibold text-white transition-all hover:bg-white/10"
                        @click="isMobileMenuOpen = false"
                    >
                        Sign Up
                    </RouterLink>
                    <RouterLink
                        to="/login"
                        class="rounded-lg bg-linear-to-r from-cyan-400 to-white px-4 py-2 text-center font-semibold text-slate-950 transition-all hover:shadow-lg"
                        @click="isMobileMenuOpen = false"
                    >
                        Sign In
                    </RouterLink>
                </div>
            </div>
        </nav>

        <section id="home" class="relative mx-auto max-w-7xl scroll-mt-24 px-6 py-16 sm:px-8 sm:py-24">
            <div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
                <div data-reveal class="reveal">
                    <p class="mb-4 inline-flex rounded-full border border-cyan-300/30 bg-cyan-400/10 px-4 py-1 text-xs font-semibold tracking-wide text-cyan-100 shadow-lg shadow-cyan-950/20">
                        Built for Welding & Fabrication Teams
                    </p>
                    <h1 class="mb-6 max-w-3xl text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                        Manage Your Welding Business Efficiently
                    </h1>
                    <p class="mb-10 max-w-2xl text-lg leading-relaxed text-slate-300 sm:text-xl">
                        WeldTrack is a comprehensive business management system designed specifically for
                        welding and fabrication businesses. Track inventory, manage projects, process sales,
                        and keep daily operations organized in one platform.
                    </p>

                    <div class="flex flex-col gap-4 sm:flex-row">
                        <RouterLink
                            to="/signup"
                            class="rounded-xl bg-linear-to-r from-cyan-400 to-white px-8 py-3 text-lg font-semibold text-slate-950 transition-all hover:shadow-xl hover:shadow-cyan-950/30"
                        >
                            Get Started
                        </RouterLink>

                        <a
                            href="#about"
                            class="rounded-xl border-2 border-white/20 bg-white/5 px-8 py-3 text-lg font-semibold text-white transition-all hover:border-white/35 hover:bg-white/10 hover:shadow-xl hover:shadow-cyan-950/20"
                        >
                            Learn More
                        </a>
                    </div>

                    <div class="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div
                            v-for="stat in heroStats"
                            :key="stat.label"
                            class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm"
                        >
                            <p class="text-2xl font-extrabold text-white">{{ stat.value }}</p>
                            <p class="mt-1 text-sm text-slate-300">{{ stat.label }}</p>
                        </div>
                    </div>
                </div>

                <div data-reveal class="reveal rounded-3xl border border-white/10 bg-white/8 p-8 shadow-2xl shadow-slate-950/40 backdrop-blur-xl">
                    <div class="mb-6 flex items-center justify-between">
                        <div>
                            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">Dashboard preview</p>
                            <h2 class="mt-1 text-xl font-bold text-white">Core Features</h2>
                        </div>
                        <span class="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold text-slate-100">3 Modules</span>
                    </div>
                    <div class="space-y-5">
                        <div
                            v-for="feature in features"
                            :key="feature.title"
                            class="reveal rounded-2xl border border-white/10 bg-slate-950/30 p-4 transition-all hover:-translate-y-0.5 hover:bg-white/10"
                            data-reveal
                        >
                            <div class="flex items-start gap-4">
                                <div
                                    :class="feature.accent"
                                    class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-xl font-bold text-slate-950 shadow-lg shadow-slate-950/20"
                                >
                                    {{ feature.icon }}
                                </div>
                                <div>
                                    <h3 class="mb-1 text-lg font-semibold text-white">{{ feature.title }}</h3>
                                    <p class="text-sm leading-relaxed text-slate-300">{{ feature.description }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="about" class="scroll-mt-24 border-y border-white/10 bg-slate-900/70 py-16 sm:py-20 backdrop-blur-sm">
            <div class="mx-auto max-w-7xl px-6 sm:px-8">
                <div class="mx-auto mb-12 max-w-2xl text-center">
                    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">Why Choose WeldTrack?</p>
                    <h2 class="mt-3 text-3xl font-extrabold tracking-tight sm:text-4xl">Designed for busy teams that need clarity fast.</h2>
                </div>

                <div class="grid grid-cols-1 gap-8 md:grid-cols-3">
                    <div
                        v-for="highlight in highlights"
                        :key="highlight.title"
                        class="reveal rounded-3xl border border-white/10 bg-white/8 p-6 shadow-xl shadow-slate-950/20 transition-all hover:-translate-y-1 hover:bg-white/12"
                        data-reveal
                    >
                        <div class="mb-4 text-4xl">{{ highlight.icon }}</div>
                        <h3 class="mb-3 text-xl font-bold text-white">{{ highlight.title }}</h3>
                        <p class="leading-relaxed text-slate-300">{{ highlight.description }}</p>
                    </div>
                </div>
            </div>
        </section>

        <section id="services" class="scroll-mt-24 py-16 sm:py-20">
            <div class="mx-auto max-w-7xl px-6 sm:px-8">
                <div class="mx-auto mb-8 max-w-2xl text-center">
                    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">Services</p>
                    <h2 class="mt-3 text-3xl font-extrabold tracking-tight sm:text-4xl">What We Offer</h2>
                    <p class="mt-2 text-slate-300">Core service offerings for welding and fabrication.</p>
                </div>

                <div v-if="services.length === 0" class="mx-auto max-w-4xl rounded-2xl border border-white/10 bg-white/6 p-8 text-center">
                    <p class="text-slate-300">Loading services...</p>
                </div>

                <div v-else class="relative mx-auto max-w-4xl">
                    <div class="overflow-hidden rounded-2xl border border-white/10 bg-white/6 p-4">
                        <div class="relative h-64 overflow-hidden rounded-xl bg-slate-900 sm:h-80">
                            <img :key="currentSlide" :src="services[currentSlide]?.image_url || 'https://via.placeholder.com/1200x800'" :alt="services[currentSlide]?.name" class="absolute inset-0 h-full w-full object-cover object-center" width="1200" height="800" />
                            <div class="absolute bottom-4 left-4 rounded-md bg-black/50 px-4 py-2 text-white">
                                <h3 class="font-bold">{{ services[currentSlide]?.name }} — {{ formatCurrency(services[currentSlide]?.price || 0) }}</h3>
                                <p class="text-sm text-slate-200">{{ services[currentSlide]?.description || 'Professional welding and fabrication service' }}</p>
                            </div>
                        </div>

                        <div class="mt-4 flex items-center justify-between gap-4">
                            <div class="flex gap-2">
                                <button @click="prevSlide" class="rounded-lg border border-white/20 px-3 py-2 bg-white/5 text-white">Prev</button>
                                <button @click="nextSlide" class="rounded-lg border border-white/20 px-3 py-2 bg-white/5 text-white">Next</button>
                            </div>

                            <div class="flex items-center gap-2">
                                <button
                                    v-for="(s, i) in services"
                                    :key="s.id"
                                    @click="currentSlide = i"
                                    :class="['h-2 w-8 rounded-full', currentSlide === i ? 'bg-cyan-400' : 'bg-white/20']"
                                ></button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="contact" class="scroll-mt-24 border-t border-white/10 bg-slate-950/70 py-14 sm:py-16">
            <div class="mx-auto max-w-7xl px-6 sm:px-8">
                <div data-reveal class="reveal mx-auto max-w-3xl rounded-3xl border border-white/10 bg-white/8 p-8 text-center shadow-2xl shadow-slate-950/30 backdrop-blur-xl">
                    <h2 class="mb-3 text-3xl font-extrabold tracking-tight">Contact Us</h2>
                    <p class="mb-6 text-slate-300">
                        Have questions about WeldTrack? Reach out and our team will help you get started.
                    </p>
                    <div class="space-y-2 text-slate-300">
                        <p><span class="font-semibold text-white">Email:</span> Goboleweldingshopadmin@gmail.com</p>
                        <p><span class="font-semibold text-white">Phone:</span> +63 935 770 5022</p>
                        <p><span class="font-semibold text-white">Address:</span> Sta. Remedios Purok - 2 Sampaloc, Bulan Sorsogon</p>
                    </div>
                </div>
            </div>
        </section>

        <footer class="border-t border-white/10 bg-slate-950 py-8">
            <div class="mx-auto max-w-7xl px-6 text-center text-slate-400 sm:px-8">
                <p>&copy; 2026 WeldTrack. All rights reserved.</p>
            </div>
        </footer>
    </div>
</template>

<style>
html {
  scroll-behavior: smooth;
}

.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 560ms ease, transform 560ms ease;
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* Services carousel tweaks */
.carousel-controls button {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.12);
    color: #fff;
}

@media (max-width: 640px) {
    .h-64 { height: 18rem; }
}
</style>
