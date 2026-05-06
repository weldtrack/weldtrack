<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

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

let observer: IntersectionObserver | null = null
const isMobileMenuOpen = ref(false)

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

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
})
</script>

<template>
    <div class="min-h-screen bg-linear-to-br from-blue-600 via-blue-700 to-blue-800 text-white">
        <nav class="sticky top-0 z-20 border-b border-blue-400/60 bg-blue-800/70 px-6 py-4 backdrop-blur sm:px-8">
            <div class="mx-auto flex max-w-7xl items-center justify-between gap-4">
                <div class="text-2xl font-extrabold tracking-tight">⚙️ WeldTrack</div>

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
                    <a href="#home" class="text-sm font-semibold text-blue-100 transition-colors hover:text-white">Home</a>
                    <a href="#about" class="text-sm font-semibold text-blue-100 transition-colors hover:text-white">About</a>
                    <a href="#contact" class="text-sm font-semibold text-blue-100 transition-colors hover:text-white">Contact</a>
                </div>

                <div class="hidden items-center gap-3 sm:flex">
                    <RouterLink
                        to="/signup"
                        class="flex-1 rounded-lg border border-white/30 px-5 py-2 text-center font-semibold text-white transition-all hover:bg-white/10 hover:shadow-lg hover:shadow-blue-950/20 sm:flex-none"
                    >
                        Sign Up
                    </RouterLink>

                    <RouterLink
                        to="/login"
                        class="flex-1 rounded-lg bg-white px-6 py-2 text-center font-semibold text-blue-700 transition-all hover:bg-gray-100 hover:shadow-lg hover:shadow-blue-950/20 sm:flex-none"
                    >
                        Sign In
                    </RouterLink>
                </div>
            </div>

            <div v-if="isMobileMenuOpen" class="mx-auto mt-4 max-w-7xl space-y-3 sm:hidden">
                <a href="#home" class="block rounded-lg border border-white/20 bg-white/5 px-4 py-2 font-semibold text-blue-100" @click="isMobileMenuOpen = false">Home</a>
                <a href="#about" class="block rounded-lg border border-white/20 bg-white/5 px-4 py-2 font-semibold text-blue-100" @click="isMobileMenuOpen = false">About</a>
                <a href="#contact" class="block rounded-lg border border-white/20 bg-white/5 px-4 py-2 font-semibold text-blue-100" @click="isMobileMenuOpen = false">Contact</a>
                <div class="grid grid-cols-2 gap-3 pt-1">
                    <RouterLink
                        to="/signup"
                        class="rounded-lg border border-white/30 px-4 py-2 text-center font-semibold text-white transition-all hover:bg-white/10"
                        @click="isMobileMenuOpen = false"
                    >
                        Sign Up
                    </RouterLink>
                    <RouterLink
                        to="/login"
                        class="rounded-lg bg-white px-4 py-2 text-center font-semibold text-blue-700 transition-all hover:bg-gray-100"
                        @click="isMobileMenuOpen = false"
                    >
                        Sign In
                    </RouterLink>
                </div>
            </div>
        </nav>

        <section id="home" class="mx-auto max-w-7xl scroll-mt-24 px-6 py-16 sm:px-8 sm:py-24">
            <div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
                <div data-reveal class="reveal">
                    <p class="mb-4 inline-flex rounded-full border border-white/25 bg-white/10 px-4 py-1 text-xs font-semibold tracking-wide text-blue-100">
                        Built for Welding & Fabrication Teams
                    </p>
                    <h1 class="mb-6 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                        Manage Your Welding Business Efficiently
                    </h1>
                    <p class="mb-10 max-w-2xl text-lg leading-relaxed text-blue-100 sm:text-xl">
                        WeldTrack is a comprehensive business management system designed specifically for
                        welding and fabrication businesses. Track inventory, manage projects, process sales,
                        and keep daily operations organized in one platform.
                    </p>

                    <div class="flex flex-col gap-4 sm:flex-row">
                        <RouterLink
                            to="/signup"
                            class="rounded-lg bg-white px-8 py-3 text-lg font-semibold text-blue-700 transition-all hover:bg-gray-100 hover:shadow-xl hover:shadow-blue-950/20"
                        >
                            Get Started
                        </RouterLink>

                        <a
                            href="#about"
                            class="rounded-lg border-2 border-white/80 px-8 py-3 text-lg font-semibold text-white transition-all hover:bg-blue-700 hover:shadow-xl hover:shadow-blue-950/20"
                        >
                            Learn More
                        </a>
                    </div>
                </div>

                <div data-reveal class="reveal rounded-2xl border border-blue-300/50 bg-linear-to-b from-blue-500/35 to-blue-700/30 p-8 shadow-2xl shadow-blue-950/30">
                    <div class="mb-6 flex items-center justify-between">
                        <h2 class="text-xl font-bold">Core Features</h2>
                        <span class="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold text-blue-100">3 Modules</span>
                    </div>
                    <div class="space-y-5">
                        <div
                            v-for="feature in features"
                            :key="feature.title"
                            class="reveal rounded-xl border border-blue-300/30 bg-white/5 p-4 transition-all hover:bg-white/10"
                            data-reveal
                        >
                            <div class="flex items-start gap-4">
                                <div
                                    :class="feature.accent"
                                    class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg text-xl font-bold text-blue-800"
                                >
                                    {{ feature.icon }}
                                </div>
                                <div>
                                    <h3 class="mb-1 text-lg font-semibold">{{ feature.title }}</h3>
                                    <p class="text-sm leading-relaxed text-blue-100">{{ feature.description }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="about" class="scroll-mt-24 bg-blue-900/45 py-16 sm:py-20">
            <div class="mx-auto max-w-7xl px-6 sm:px-8">
                <h2 class="mb-12 text-center text-3xl font-extrabold tracking-tight sm:text-4xl">Why Choose WeldTrack?</h2>

                <div class="grid grid-cols-1 gap-8 md:grid-cols-3">
                    <div
                        v-for="highlight in highlights"
                        :key="highlight.title"
                        class="reveal rounded-2xl border border-blue-300/40 bg-white/10 p-6 shadow-xl shadow-blue-950/15 transition-all hover:-translate-y-1 hover:bg-white/15"
                        data-reveal
                    >
                        <div class="mb-4 text-4xl">{{ highlight.icon }}</div>
                        <h3 class="mb-3 text-xl font-bold">{{ highlight.title }}</h3>
                        <p class="leading-relaxed text-blue-100">{{ highlight.description }}</p>
                    </div>
                </div>
            </div>
        </section>

        <section id="contact" class="scroll-mt-24 border-t border-blue-400/30 bg-blue-800/40 py-14 sm:py-16">
            <div class="mx-auto max-w-7xl px-6 sm:px-8">
                <div data-reveal class="reveal mx-auto max-w-3xl rounded-2xl border border-blue-300/40 bg-white/10 p-8 text-center">
                    <h2 class="mb-3 text-3xl font-extrabold tracking-tight">Contact Us</h2>
                    <p class="mb-6 text-blue-100">
                        Have questions about WeldTrack? Reach out and our team will help you get started.
                    </p>
                    <div class="space-y-2 text-blue-100">
                        <p><span class="font-semibold text-white">Email:</span> support@weldtrack.com</p>
                        <p><span class="font-semibold text-white">Phone:</span> +63 912 345 6789</p>
                        <p><span class="font-semibold text-white">Address:</span> Bicol Region, Philippines</p>
                    </div>
                </div>
            </div>
        </section>

        <footer class="border-t border-blue-400/50 bg-blue-900 py-8">
            <div class="mx-auto max-w-7xl px-6 text-center text-blue-200 sm:px-8">
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
</style>
