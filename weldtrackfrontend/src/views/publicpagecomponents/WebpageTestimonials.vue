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
    <section class="relative bg-public-bg py-16 sm:py-24 border-t border-slate-800/60">
        <div class="mx-auto max-w-7xl px-6 sm:px-10">
            <div data-reveal class="reveal mx-auto max-w-2xl text-center">
                <p class="text-xs font-semibold uppercase tracking-wider text-sky-400">Testimonials</p>
                <h2 class="mt-3 text-3xl font-bold tracking-tight text-[color:var(--public-text)] sm:text-4xl">Trusted by customers</h2>
                <p class="mt-3 text-base text-slate-400">See what customers say about their experience using WeldTrack.</p>
            </div>

            <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                <div v-for="(testimonial, idx) in testimonials" :key="idx" data-reveal class="reveal flex flex-col rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm transition hover:border-slate-700">
                    <div class="flex gap-1 text-amber-400 mb-4">
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                        <Star class="h-4 w-4 fill-current" />
                    </div>
                    <blockquote class="flex-1 text-sm leading-6 text-slate-300">
                        "{{ testimonial.quote }}"
                    </blockquote>
                    <div class="mt-6 flex items-center gap-3 border-t border-slate-800/60 pt-4">
                        <div class="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-white">
                            {{ testimonial.name.charAt(0) }}
                        </div>
                        <div>
                            <div class="text-xs font-bold text-white">{{ testimonial.name }}</div>
                            <div class="text-[11px] text-slate-400">{{ testimonial.role }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
