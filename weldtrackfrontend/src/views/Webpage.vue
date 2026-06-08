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
        title: 'Inventory Management',
        description: 'Track materials, monitor stock levels, and manage low-stock alerts with precision.',
    },
    {
        icon: '🛠️',
        accent: 'bg-green-400/20 text-green-500',
        title: 'Project Tracking',
        description: 'Manage projects from conception to completion with detailed timelines and status updates.',
    },
    {
        icon: '📊',
        accent: 'bg-red-400/20 text-red-500',
        title: 'Sales Tracking',
        description: 'Record transactions and generate detailed business reports to drive growth.',
    },
]

const highlights = [
    {
        icon: '🎯',
        title: 'Role-Based Access',
        description: 'Customized interfaces for admins, staff, and customers to streamline every workflow.',
    },
    {
        icon: '⚡',
        title: 'Real-Time Updates',
        description: 'Instant notifications and live data synchronization across all devices and users.',
    },
    {
        icon: '🔒',
        title: 'Secure & Reliable',
        description: 'Enterprise-grade security with encrypted data protection and role-based permissions.',
    },
]

const heroStats = [
    { value: '24/7', label: 'Visibility' },
    { value: '100%', label: 'Secure' },
    { value: '1', label: 'Platform' },
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
        <section id="home" class="relative mx-auto max-w-7xl px-6 py-20 sm:px-12 lg:py-32">
            <div class="flex flex-col items-center text-center">
                <div data-reveal class="reveal mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-1.5 text-xs font-bold tracking-widest text-cyan-400 uppercase">
                    <span class="relative flex h-2 w-2">
                        <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-75"></span>
                        <span class="relative inline-flex h-2 w-2 rounded-full bg-cyan-500"></span>
                    </span>
                    The Future of Fabrication
                </div>
                
                <h1 data-reveal class="reveal mb-8 max-w-4xl text-5xl font-black leading-[1.1] tracking-tight sm:text-6xl lg:text-7xl">
                    Precision Management for <span class="bg-linear-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Welding Teams</span>
                </h1>
                
                <p data-reveal class="reveal mb-12 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
                    Streamline your entire fabrication workflow. Track inventory, manage projects, and scale your business with the only platform built specifically for welding professionals.
                </p>

                <div data-reveal class="reveal flex flex-col items-center gap-5 sm:flex-row">
                    <RouterLink
                        to="/signup"
                        class="group relative flex h-14 items-center justify-center overflow-hidden rounded-full bg-linear-to-br from-cyan-500 to-blue-600 px-10 text-lg font-bold text-white transition-all hover:scale-[1.02] hover:shadow-2xl hover:shadow-cyan-500/25 active:scale-95"
                    >
                        <span>Start Your Free Trial</span>
                        <div class="ml-2 transition-transform group-hover:translate-x-1">→</div>
                    </RouterLink>
                    <a
                        href="#about"
                        class="flex h-14 items-center justify-center rounded-full border border-white/10 bg-white/5 px-10 text-lg font-semibold text-white transition-all hover:bg-white/10 active:scale-95"
                    >
                        See How It Works
                    </a>
                </div>

                <!-- Hero Stats -->
                <div data-reveal class="reveal mt-20 grid grid-cols-1 gap-8 sm:grid-cols-3 sm:gap-16">
                    <div v-for="stat in heroStats" :key="stat.label" class="flex flex-col items-center">
                        <div class="text-4xl font-black text-white">{{ stat.value }}</div>
                        <div class="mt-1 text-sm font-bold tracking-widest text-slate-500 uppercase">{{ stat.label }}</div>
                    </div>
                </div>
            </div>

            <!-- UI Preview -->
            <div data-reveal class="reveal mt-24 relative mx-auto max-w-5xl">
                <div class="absolute -inset-1 rounded-[2.5rem] bg-linear-to-r from-cyan-500 to-blue-600 opacity-20 blur-2xl"></div>
                <div class="relative overflow-hidden rounded-[2rem] border border-white/10 bg-[#0f172a]/80 p-4 shadow-2xl backdrop-blur-xl">
                    <div class="flex items-center justify-between border-b border-white/5 pb-4 mb-6">
                        <div class="flex gap-2">
                            <div class="h-3 w-3 rounded-full bg-red-500/50"></div>
                            <div class="h-3 w-3 rounded-full bg-yellow-500/50"></div>
                            <div class="h-3 w-3 rounded-full bg-green-500/50"></div>
                        </div>
                        <div class="px-4 py-1 rounded-full bg-white/5 text-[10px] font-bold tracking-widest text-slate-500 uppercase">WeldTrack Dashboard</div>
                        <div class="w-12"></div>
                    </div>
                    
                    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
                        <div v-for="feature in features" :key="feature.title" class="flex flex-col gap-4 rounded-2xl bg-[#020617]/50 p-6 border border-white/5 hover:border-white/10 transition-colors">
                            <div :class="feature.accent" class="flex h-12 w-12 items-center justify-center rounded-xl text-2xl">
                                {{ feature.icon }}
                            </div>
                            <div>
                                <h3 class="text-lg font-bold text-white mb-2">{{ feature.title }}</h3>
                                <p class="text-sm text-slate-400 leading-relaxed">{{ feature.description }}</p>
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
                        <div data-reveal class="reveal mb-4 text-sm font-bold tracking-[0.3em] text-cyan-500 uppercase">The WeldTrack Edge</div>
                        <h2 data-reveal class="reveal mb-8 text-4xl font-extrabold tracking-tight text-white sm:text-5xl">Built by fabricators, for fabricators.</h2>
                        <p data-reveal class="reveal mb-12 text-lg leading-relaxed text-slate-400">
                            We understood that general management software doesn't cut it for the welding industry. WeldTrack was built to handle the unique complexities of material tracking, complex project timelines, and multi-role team management.
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
                            alt="Welding Workshop" 
                            class="relative rounded-[2.5rem] border border-white/10 shadow-2xl grayscale hover:grayscale-0 transition-all duration-700"
                        />
                        <div class="absolute -bottom-5 left-4 flex max-w-[9.5rem] flex-col gap-1 rounded-2xl bg-linear-to-br from-cyan-500 to-blue-600 p-4 shadow-2xl sm:-bottom-8 sm:-left-8 sm:max-w-none sm:gap-2 sm:rounded-3xl sm:p-8">
                            <div class="text-2xl font-black text-white sm:text-4xl">10x</div>
                            <div class="text-[10px] font-bold uppercase tracking-widest text-white/80 sm:text-sm">Efficiency Gain</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Services Section -->
        <section id="services" class="py-24 sm:py-32">
            <div class="mx-auto max-w-7xl px-6 sm:px-12 text-center">
                <div data-reveal class="reveal mb-4 text-sm font-bold tracking-[0.3em] text-cyan-500 uppercase">Core Capabilities</div>
                <h2 data-reveal class="reveal mb-16 text-4xl font-extrabold tracking-tight text-white sm:text-5xl">Our Service Offerings</h2>

                <div v-if="services.length === 0" class="mx-auto max-w-xl py-20">
                    <div class="flex flex-col items-center gap-4">
                        <div class="h-10 w-10 animate-spin rounded-full border-2 border-white/5 border-t-cyan-500"></div>
                        <p class="text-slate-400">Fetching latest services...</p>
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
                                        <p class="max-w-xl text-lg text-slate-300 leading-relaxed">{{ services[currentSlide]?.description || 'High-performance welding solution tailored to your industrial requirements.' }}</p>
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
                <div data-reveal class="reveal relative overflow-hidden rounded-[3rem] bg-linear-to-br from-cyan-600 to-blue-700 p-12 sm:p-20 text-center shadow-2xl shadow-cyan-950/40">
                    <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
                    <div class="relative z-10">
                        <h2 class="mb-6 text-4xl font-black tracking-tight text-white sm:text-6xl">Ready to optimize your <br class="hidden sm:block">fabrication shop?</h2>
                        <p class="mx-auto mb-12 max-w-2xl text-lg font-medium text-cyan-50/80 sm:text-xl">
                            Join over 500+ teams using WeldTrack to streamline their daily operations.
                        </p>
                        <div class="flex flex-col items-center justify-center gap-6 sm:flex-row">
                            <RouterLink 
                                to="/signup" 
                                class="flex h-16 items-center justify-center rounded-full bg-white px-10 text-lg font-black text-cyan-600 transition-all hover:scale-105 hover:shadow-2xl active:scale-95"
                            >
                                Get Started Today
                            </RouterLink>
                            <div class="text-white/80">
                                <div class="text-sm font-bold uppercase tracking-widest mb-1 text-white">Direct Support</div>
                                <div class="text-xl font-bold">+63 935 770 5022</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-20 grid grid-cols-1 gap-12 text-center lg:grid-cols-3">
                    <div>
                        <div class="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2">Email</div>
                        <div class="text-lg font-semibold text-white">Goboleweldingshopadmin@gmail.com</div>
                    </div>
                    <div>
                        <div class="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2">Location</div>
                        <div class="text-lg font-semibold text-white">Sta. Remedios, Bulan Sorsogon</div>
                    </div>
                    <div>
                        <div class="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2">Operating Hours</div>
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
