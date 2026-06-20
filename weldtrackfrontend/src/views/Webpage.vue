<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import api from '../services/api'
import ThemeToggle from '../components/ui/ThemeToggle.vue'
import { useThemeMode } from '../composables/useThemeMode'

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
        accent: 'bg-yellow-400/20 text-yellow-500',
        title: 'Easy Booking',
        description: 'Request welding services in a few simple steps from your customer account.',
    },
    {
        icon: '🛠️',
        accent: 'bg-green-400/20 text-green-500',
        title: 'Live Status',
        description: 'See updates on your request as it moves through the service process.',
    },
    {
        icon: '📊',
        accent: 'bg-red-400/20 text-red-500',
        title: 'Secure Account',
        description: 'Keep your details and booking history organized in one secure place.',
    },
]

const highlights = [
    {
        icon: '🎯',
        title: 'Simple Booking Flow',
        description: 'Create an account, choose a service, and submit your request without confusion.',
    },
    {
        icon: '⚡',
        title: 'Fast Updates',
        description: 'Follow your booking status and get updates without needing to call around.',
    },
    {
        icon: '🔒',
        title: 'Private & Reliable',
        description: 'Your account details and service requests stay protected and easy to access.',
    },
]

const heroStats = [
    { value: '3', label: 'Simple steps' },
    { value: '24/7', label: 'Booking access' },
    { value: '1', label: 'Customer portal' },
]

let observer: IntersectionObserver | null = null
const isMobileMenuOpen = ref(false)
const { isDarkMode } = useThemeMode()

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
  autoplayTimer = window.setInterval(nextSlide, 5000)
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
    { threshold: 0.1, rootMargin: '0px 0px -50px 0px' },
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
    <div :class="['public-theme-page relative min-h-screen overflow-hidden bg-[#020617] text-slate-50 selection:bg-cyan-500/30', isDarkMode ? 'theme-dark' : 'theme-light']">
        <!-- Background Elements -->
        <div class="pointer-events-none absolute inset-0 overflow-hidden">
            <div class="absolute -left-[10%] top-[-10%] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-[120px]"></div>
            <div class="absolute -right-[5%] top-[20%] h-[600px] w-[600px] rounded-full bg-blue-600/10 blur-[140px]"></div>
            <div class="absolute bottom-[-10%] left-[20%] h-[400px] w-[400px] rounded-full bg-emerald-500/5 blur-[100px]"></div>
            <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
        </div>

        <!-- Navigation -->
        <nav class="public-nav sticky top-0 z-50 border-b border-white/5 bg-[#020617]/80 px-6 py-4 backdrop-blur-md transition-all sm:px-12">
            <div class="mx-auto flex max-w-7xl items-center justify-between">
                <div class="flex items-center gap-2.5">
                    <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-linear-to-br from-cyan-400 to-blue-600 p-0.5 shadow-lg shadow-cyan-500/20">
                        <div class="flex h-full w-full items-center justify-center rounded-[10px] bg-[#020617] text-lg">
                            ⚙️
                        </div>
                    </div>
                    <span class="text-xl font-bold tracking-tight">WeldTrack</span>
                </div>

                <div class="hidden items-center gap-10 lg:flex">
                    <a href="#home" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Home</a>
                    <a href="#about" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Why WeldTrack</a>
                    <a href="#services" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Services</a>
                    <a href="#contact" class="text-[15px] font-medium text-slate-400 transition-colors hover:text-white">Contact</a>
                </div>

                <div class="hidden items-center gap-4 lg:flex">
                    <ThemeToggle />
                    <RouterLink
                        to="/login"
                        class="text-[15px] font-semibold text-slate-300 transition-colors hover:text-white"
                    >
                        Sign In
                    </RouterLink>
                    <RouterLink
                        to="/signup"
                        class="rounded-full bg-slate-50 px-6 py-2 text-[15px] font-bold text-[#020617] transition-all hover:bg-white hover:shadow-xl hover:shadow-white/10 active:scale-95"
                    >
                        Get Started
                    </RouterLink>
                </div>

                <button
                    type="button"
                    class="flex h-10 w-10 items-center justify-center rounded-lg bg-white/5 text-white lg:hidden"
                    @click="isMobileMenuOpen = !isMobileMenuOpen"
                >
                    <svg v-if="!isMobileMenuOpen" class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                    <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <!-- Mobile Menu -->
            <div v-if="isMobileMenuOpen" class="public-mobile-menu absolute left-0 top-full w-full border-b border-white/5 bg-[#020617] px-6 py-8 space-y-6 lg:hidden">
                <div class="flex justify-end">
                    <ThemeToggle />
                </div>
                <div class="flex flex-col gap-6">
                    <a href="#home" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Home</a>
                    <a href="#about" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Why WeldTrack</a>
                    <a href="#services" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Services</a>
                    <a href="#contact" class="text-lg font-medium text-slate-300" @click="isMobileMenuOpen = false">Contact</a>
                </div>
                <div class="flex flex-col gap-4 pt-4 border-t border-white/5">
                    <RouterLink to="/login" class="flex h-12 items-center justify-center font-semibold text-white" @click="isMobileMenuOpen = false">Sign In</RouterLink>
                    <RouterLink to="/signup" class="flex h-12 items-center justify-center rounded-xl bg-slate-50 font-bold text-[#020617]" @click="isMobileMenuOpen = false">Get Started</RouterLink>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <section id="home" class="public-hero relative mx-auto max-w-7xl px-6 py-20 sm:px-12 lg:py-28">
            <div class="grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16">
                <div class="relative z-10 max-w-2xl text-center lg:text-left">
                    <div data-reveal class="reveal mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-1.5 text-xs font-bold tracking-widest text-cyan-400 uppercase">
                        <span class="relative flex h-2 w-2">
                            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-75"></span>
                            <span class="relative inline-flex h-2 w-2 rounded-full bg-cyan-500"></span>
                        </span>
                        Customer Service Booking
                    </div>

                    <h1 data-reveal class="public-hero-title reveal mb-8 text-5xl font-black leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl">
                        Book Welding Services <span class="bg-linear-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">with Ease</span>
                    </h1>

                    <p data-reveal class="public-hero-copy reveal mb-10 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
                        Create your customer account, schedule a service, and track your bookings in one place. WeldTrack is built for customers who want a faster way to request welding work.
                    </p>

                    <div data-reveal class="reveal flex flex-col items-center gap-5 sm:flex-row lg:justify-start">
                        <RouterLink
                            to="/signup"
                            class="group relative flex h-14 items-center justify-center overflow-hidden rounded-full bg-linear-to-br from-cyan-500 to-blue-600 px-10 text-lg font-bold text-white transition-all hover:scale-[1.02] hover:shadow-2xl hover:shadow-cyan-500/25 active:scale-95"
                        >
                            <span>Get Started</span>
                            <div class="ml-2 transition-transform group-hover:translate-x-1">→</div>
                        </RouterLink>
                        <a
                            href="#contact"
                            class="flex h-14 items-center justify-center rounded-full border border-white/10 bg-white/5 px-10 text-lg font-semibold text-white transition-all hover:bg-white/10 active:scale-95"
                        >
                            Contact Us
                        </a>
                    </div>

                    <div data-reveal class="reveal mt-12 grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div v-for="stat in heroStats" :key="stat.label" class="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-left backdrop-blur-md">
                            <div class="text-3xl font-black text-white">{{ stat.value }}</div>
                            <div class="mt-1 text-xs font-bold tracking-[0.22em] text-slate-400 uppercase">{{ stat.label }}</div>
                        </div>
                    </div>
                </div>

                <div data-reveal class="public-hero-visual reveal relative mx-auto w-full max-w-[38rem]">
                    <div class="public-hero-glow absolute -inset-8 rounded-[2.5rem] bg-linear-to-r from-cyan-500/20 via-blue-500/15 to-emerald-500/10 blur-3xl"></div>
                    <div class="relative overflow-hidden rounded-[2.25rem] border border-white/10 bg-[#0f172a]/75 shadow-2xl backdrop-blur-xl">
                        <div class="absolute inset-0 bg-[linear-gradient(180deg,rgba(8,15,32,0.2)_0%,rgba(2,6,23,0.75)_100%)]"></div>
                        <img
                            src="https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1600&auto=format&fit=crop"
                            alt="Customer booking experience"
                            class="public-hero-image h-[34rem] w-full object-cover sm:h-[40rem]"
                        />
                        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.16),transparent_42%),linear-gradient(180deg,transparent_20%,rgba(2,6,23,0.84)_100%)]"></div>

                        <div class="absolute left-5 top-5 flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/70 px-4 py-2 text-xs font-bold tracking-[0.2em] text-cyan-200 uppercase backdrop-blur-md">
                            Live visibility
                        </div>

                        <div class="absolute bottom-5 left-5 right-5 grid gap-3 sm:grid-cols-[1.2fr_0.8fr]">
                        <div class="public-hero-card hero-float rounded-2xl border border-white/10 bg-slate-950/70 p-4 backdrop-blur-md">
                                <div class="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Customer flow</div>
                                <div class="mt-1 text-xl font-black text-white">Book, confirm, follow up</div>
                                <div class="mt-2 text-sm text-slate-300">A clean path from account creation to service booking.</div>
                            </div>
                            <div class="public-hero-card hero-float-delayed rounded-2xl border border-white/10 bg-cyan-500/15 p-4 backdrop-blur-md">
                                <div class="text-xs font-bold uppercase tracking-[0.22em] text-cyan-200">Booking time</div>
                                <div class="mt-1 text-2xl font-black text-white">&lt; 1 min</div>
                                <div class="mt-2 text-sm text-cyan-50/80">Fast access to customer requests.</div>
                            </div>
                        </div>

                        <div class="absolute right-5 top-1/2 hidden -translate-y-1/2 gap-3 lg:flex lg:flex-col">
                            <div v-for="feature in features" :key="feature.title" class="hero-feature-card hero-pulse rounded-2xl border border-white/10 bg-slate-950/70 p-4 shadow-xl backdrop-blur-md">
                                <div :class="feature.accent" class="flex h-10 w-10 items-center justify-center rounded-xl text-xl">
                                    {{ feature.icon }}
                                </div>
                                <div class="mt-3 max-w-[12rem]">
                                    <div class="text-sm font-bold text-white">{{ feature.title }}</div>
                                    <div class="mt-1 text-xs leading-relaxed text-slate-400">{{ feature.description }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Why Choose Section -->
        <section id="about" class="relative bg-[#020617] py-24 sm:py-32">
            <div class="mx-auto max-w-7xl px-6 sm:px-12">
                <div class="grid grid-cols-1 gap-16 lg:grid-cols-2 lg:items-center">
                    <div>
                        <div data-reveal class="reveal mb-4 text-sm font-bold tracking-[0.3em] text-cyan-500 uppercase">Why Customers Use WeldTrack</div>
                        <h2 data-reveal class="reveal mb-8 text-4xl font-extrabold tracking-tight text-white sm:text-5xl">Built to make booking easier.</h2>
                        <p data-reveal class="reveal mb-12 text-lg leading-relaxed text-slate-400">
                            WeldTrack gives customers one place to create an account, request welding services, and keep track of everything that matters.
                        </p>
                        
                        <div class="space-y-8">
                            <div v-for="highlight in highlights" :key="highlight.title" data-reveal class="reveal flex gap-5">
                                <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white/5 text-2xl shadow-inner border border-white/5">
                                    {{ highlight.icon }}
                                </div>
                                <div>
                                    <h3 class="mb-1 text-xl font-bold text-white">{{ highlight.title }}</h3>
                                    <p class="text-slate-400">{{ highlight.description }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div data-reveal class="reveal relative lg:ml-auto">
                        <div class="absolute -inset-10 rounded-full bg-blue-500/10 blur-[100px]"></div>
                        <img 
                            src="https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=2070&auto=format&fit=crop" 
                            alt="Customer browsing service options" 
                            class="relative rounded-[2.5rem] border border-white/10 shadow-2xl grayscale hover:grayscale-0 transition-all duration-700"
                        />
                        <div class="absolute -bottom-5 left-4 flex max-w-[9.5rem] flex-col gap-1 rounded-2xl bg-linear-to-br from-cyan-500 to-blue-600 p-4 shadow-2xl sm:-bottom-8 sm:-left-8 sm:max-w-none sm:gap-2 sm:rounded-3xl sm:p-8">
                            <div class="text-2xl font-black text-white sm:text-4xl">10x</div>
                            <div class="text-[10px] font-bold uppercase tracking-widest text-white/80 sm:text-sm">Faster booking</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Services Section -->
        <section id="services" class="py-24 sm:py-32">
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
                    <div class="group relative overflow-hidden rounded-[2.5rem] border border-white/10 bg-[#0f172a]/50 p-6 backdrop-blur-sm">
                        <div class="relative h-[400px] sm:h-[500px] overflow-hidden rounded-[1.5rem] shadow-2xl">
                            <transition name="fade" mode="out-in">
                                <div :key="currentSlide" class="h-full w-full">
                                    <img 
                                        :src="services[currentSlide]?.image_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2164&auto=format&fit=crop'" 
                                        :alt="services[currentSlide]?.name" 
                                        class="h-full w-full object-cover transition-transform duration-[2000ms] group-hover:scale-110"
                                    />
                                    <div class="absolute inset-0 bg-linear-to-t from-[#020617] via-transparent to-transparent"></div>
                                    <div class="absolute bottom-10 left-10 right-10 text-left">
                                        <div class="mb-2 inline-block rounded-full bg-cyan-500/20 px-4 py-1 text-xs font-bold tracking-widest text-cyan-400 uppercase backdrop-blur-md">
                                            {{ formatCurrency(services[currentSlide]?.price || 0) }}
                                        </div>
                                        <h3 class="mb-4 text-4xl font-black text-white">{{ services[currentSlide]?.name }}</h3>
                                        <p class="max-w-xl text-lg text-slate-300 leading-relaxed">{{ services[currentSlide]?.description || 'A service option customers can book directly from the portal.' }}</p>
                                    </div>
                                </div>
                            </transition>
                        </div>

                        <div class="mt-8 flex flex-col items-center justify-between gap-6 sm:flex-row">
                            <div class="flex gap-3">
                                <button @click="prevSlide" class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white transition-all hover:bg-white/10 active:scale-90">
                                    ←
                                </button>
                                <button @click="nextSlide" class="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white transition-all hover:bg-white/10 active:scale-90">
                                    →
                                </button>
                            </div>

                            <div class="flex items-center gap-2.5">
                                <button
                                    v-for="(s, i) in services"
                                    :key="s.id"
                                    @click="currentSlide = i"
                                    :class="['h-1.5 rounded-full transition-all duration-500', currentSlide === i ? 'w-10 bg-cyan-400' : 'w-4 bg-white/10 hover:bg-white/20']"
                                ></button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA/Contact Section -->
        <section id="contact" class="relative py-24 sm:py-32">
            <div class="mx-auto max-w-7xl px-6 sm:px-12">
                <div data-reveal class="public-contact-panel reveal relative overflow-hidden rounded-[3rem] border border-white/10 bg-[#0f172a]/70 p-12 shadow-2xl shadow-cyan-950/30 sm:p-20">
                    <div class="public-contact-overlay absolute inset-0 bg-[linear-gradient(135deg,rgba(8,47,73,0.55)_0%,rgba(2,6,23,0.92)_70%)]"></div>
                    <div class="public-contact-noise absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
                    <div class="relative z-10 mx-auto max-w-4xl text-center">
                        <div class="public-contact-chip mb-4 inline-flex items-center rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-1.5 text-xs font-bold tracking-[0.24em] text-cyan-300 uppercase">
                            Contact support
                        </div>
                        <h2 class="public-contact-title mb-6 text-4xl font-black tracking-tight text-white sm:text-6xl">
                            Need help <br class="hidden sm:block">with a booking?
                        </h2>
                        <p class="public-contact-copy mx-auto mb-12 max-w-2xl text-lg font-medium text-slate-300 sm:text-xl">
                            Use the details below to call, email, or visit us directly. This page is focused on customer support and booking help.
                        </p>

                        <div class="grid gap-4 sm:grid-cols-3">
                            <a
                                href="tel:+639357705022"
                                class="public-contact-card rounded-2xl border border-white/10 bg-white/5 px-5 py-5 text-left transition hover:border-cyan-400/30 hover:bg-white/10"
                            >
                                <div class="text-xs font-bold uppercase tracking-widest text-cyan-300">Direct Support</div>
                                <div class="mt-2 text-xl font-black text-white">+63 935 770 5022</div>
                                <div class="mt-1 text-sm text-slate-400">Call for quick inquiries</div>
                            </a>

                            <a
                                href="mailto:Goboleweldingshopadmin@gmail.com"
                                class="public-contact-card rounded-2xl border border-white/10 bg-white/5 px-5 py-5 text-left transition hover:border-cyan-400/30 hover:bg-white/10"
                            >
                                <div class="text-xs font-bold uppercase tracking-widest text-cyan-300">Email</div>
                                <div class="mt-2 break-words text-xl font-black text-white">Goboleweldingshopadmin@gmail.com</div>
                                <div class="mt-1 text-sm text-slate-400">Send detailed questions or requests</div>
                            </a>

                            <div class="public-contact-card rounded-2xl border border-white/10 bg-white/5 px-5 py-5 text-left">
                                <div class="text-xs font-bold uppercase tracking-widest text-cyan-300">Location</div>
                                <div class="mt-2 text-xl font-black text-white">Sta. Remedios, Bulan Sorsogon</div>
                                <div class="mt-1 text-sm text-slate-400">Visit us during business hours</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-20 flex justify-center">
                    <div class="public-contact-bottom w-full max-w-xl rounded-3xl border border-white/10 bg-white/5 px-8 py-6 text-center shadow-lg">
                        <div class="mb-2 text-sm font-bold uppercase tracking-widest text-slate-500">Operating Hours</div>
                        <div class="text-lg font-semibold text-white">Mon — Sat: 8:00 AM - 5:00 PM</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="border-t border-white/5 bg-[#020617] py-12">
            <div class="mx-auto max-w-7xl px-6 text-center sm:px-12">
                <div class="flex items-center justify-center gap-2.5 mb-8">
                    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-lg">⚙️</div>
                    <span class="text-lg font-bold tracking-tight">WeldTrack</span>
                </div>
                <p class="text-slate-500 text-sm">&copy; 2026 WeldTrack Management Systems. All rights reserved.</p>
            </div>
        </footer>
    </div>
</template>

<style scoped>
.public-hero-image {
  animation: heroImageDrift 12s ease-in-out infinite alternate;
}

.hero-float {
  animation: heroFloat 6s ease-in-out infinite;
}

.hero-float-delayed {
  animation: heroFloat 6s ease-in-out infinite;
  animation-delay: 1.4s;
}

.hero-pulse {
  animation: heroPulse 5s ease-in-out infinite;
}

@keyframes heroImageDrift {
  0% {
    transform: scale(1) translateY(0);
  }
  100% {
    transform: scale(1.04) translateY(-8px);
  }
}

@keyframes heroFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes heroPulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgb(34 211 238 / 0.16);
  }
  50% {
    box-shadow: 0 0 0 12px rgb(34 211 238 / 0);
  }
}
</style>

<style>
html {
  scroll-behavior: smooth;
}

.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 800ms cubic-bezier(0.2, 1, 0.3, 1), transform 800ms cubic-bezier(0.2, 1, 0.3, 1);
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 500ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Custom selection color */
::selection {
  background: rgba(34, 211, 238, 0.3);
  color: #fff;
}

/* Hide scrollbar for clean UI */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #020617;
}

::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #334155;
}
</style>
