<script setup lang="ts">
import { Star } from 'lucide-vue-next'

const testimonials = [
    {
        name: 'Mark Reyes',
        role: 'Homeowner',
        quote: 'WeldTrack made it incredibly easy to book a gate repair. No more calling back and forth. I just checked the portal and knew exactly when the technicians were arriving.',
    },
    {
        name: 'Sarah Gomez',
        role: 'Business Owner',
        quote: 'We needed custom metal racks for our store. The ability to track the project cost and status online gave us complete peace of mind. Highly recommended.',
    },
    {
        name: 'John Dela Cruz',
        role: 'Property Manager',
        quote: 'The automated updates are a game changer. I manage multiple properties, and knowing the status of every welding repair in one dashboard is fantastic.',
    }
]
</script>

<template>
    <section class="relative bg-public-bg py-16 sm:py-24 border-b border-slate-200/5 dark:border-white/5">
        <div class="mx-auto max-w-7xl px-6 sm:px-12">
            <div data-reveal class="reveal mx-auto max-w-2xl text-center">
                <p class="text-sm font-bold uppercase tracking-[0.3em] text-cyan-500">Testimonials</p>
                <h2 class="mt-4 text-3xl font-bold tracking-tight text-[color:var(--public-text)] sm:text-4xl">Trusted by customers</h2>
                <p class="mt-4 text-lg text-slate-500">See what others are saying about their seamless booking experience.</p>
            </div>

            <div class="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
                <div v-for="(testimonial, idx) in testimonials" :key="idx" data-reveal class="reveal flex flex-col rounded-2xl border border-slate-200/20 dark:border-white/10 bg-public-panel p-8 shadow-sm backdrop-blur-xl transition hover:border-cyan-400/30">
                    <div class="flex gap-1 text-amber-400 mb-6">
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                    </div>
                    <blockquote class="flex-1 text-base leading-7 text-slate-500 dark:text-slate-400">
                        "{{ testimonial.quote }}"
                    </blockquote>
                    <div class="mt-6 flex items-center gap-4 border-t border-slate-200/20 dark:border-white/5 pt-6">
                        <div class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-200 dark:bg-white/10 text-sm font-bold text-[color:var(--public-text)]">
                            {{ testimonial.name.charAt(0) }}
                        </div>
                        <div>
                            <div class="text-sm font-bold text-[color:var(--public-text)]">{{ testimonial.name }}</div>
                            <div class="text-xs text-slate-500">{{ testimonial.role }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
