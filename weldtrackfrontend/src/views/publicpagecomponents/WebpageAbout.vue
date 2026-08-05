<script setup lang="ts">
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
</script>

<template>
    <section id="about" class="relative bg-public-dark py-24 sm:py-32">
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
                    <img src="https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=2070&auto=format&fit=crop"
                        alt="Customer browsing service options"
                        class="relative rounded-[2.5rem] border border-white/10 shadow-2xl grayscale hover:grayscale-0 transition-all duration-700" />
                    <div class="absolute -bottom-5 left-4 flex max-w-[9.5rem] flex-col gap-1 rounded-2xl bg-linear-to-br from-cyan-500 to-blue-600 p-4 shadow-2xl sm:-bottom-8 sm:-left-8 sm:max-w-none sm:gap-2 sm:rounded-3xl sm:p-8">
                        <div class="text-2xl font-black text-white sm:text-4xl">10x</div>
                        <div class="text-[10px] font-bold uppercase tracking-widest text-white/80 sm:text-sm">Faster booking</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>