<script setup lang="ts">
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

const heroStats = [
    { value: '3', label: 'Simple steps' },
    { value: '24/7', label: 'Booking access' },
    { value: '1', label: 'Customer portal' },
]
</script>

<template>
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
                    Create your customer account, schedule a service, and track your bookings in one place.
                    WeldTrack is built for customers who want a faster way to request welding work.
                </p>

                <div data-reveal class="reveal flex flex-col items-center gap-5 sm:flex-row lg:justify-start">
                    <RouterLink to="/signup" class="group relative flex h-14 items-center justify-center overflow-hidden rounded-full bg-linear-to-br from-cyan-500 to-blue-600 px-10 text-lg font-bold text-white transition-all hover:scale-[1.02] hover:shadow-2xl hover:shadow-cyan-500/25 active:scale-95">
                        <span>Get Started</span>
                        <div class="ml-2 transition-transform group-hover:translate-x-1">→</div>
                    </RouterLink>
                    <a href="#contact" class="flex h-14 items-center justify-center rounded-full border border-white/10 bg-white/5 px-10 text-lg font-semibold text-white transition-all hover:bg-white/10 active:scale-95">
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
                    <img src="https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1600&auto=format&fit=crop"
                        alt="Customer booking experience"
                        class="public-hero-image h-[34rem] w-full object-cover sm:h-[40rem]" />
                    <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.16),transparent_42%),linear-gradient(180deg,transparent_20%,rgba(2,6,23,0.84)_100%)]"></div>

                    <div class="absolute left-5 top-5 flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/70 px-4 py-2 text-xs font-bold tracking-[0.2em] text-cyan-600 uppercase backdrop-blur-md">
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
</template>

<style scoped>
.public-hero-image { animation: heroImageDrift 12s ease-in-out infinite alternate; }
.hero-float { animation: heroFloat 6s ease-in-out infinite; }
.hero-float-delayed { animation: heroFloat 6s ease-in-out infinite; animation-delay: 1.4s; }
.hero-pulse { animation: heroPulse 5s ease-in-out infinite; }

@keyframes heroImageDrift {
    0% { transform: scale(1) translateY(0); }
    100% { transform: scale(1.04) translateY(-8px); }
}
@keyframes heroFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
@keyframes heroPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgb(34 211 238 / 0.16); }
    50% { box-shadow: 0 0 0 12px rgb(34 211 238 / 0); }
}
</style>