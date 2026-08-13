<script setup lang="ts">
import {
    ArrowRight,
    Check,
    MapPin,
    Phone,
} from 'lucide-vue-next'

const trustPoints = [
    'Local service in Bulan',
    'Upfront booking details',
    'Progress you can check online',
]
</script>

<template>
    <section id="home" class="public-hero relative mx-auto max-w-7xl px-6 pb-16 pt-24 sm:px-10 sm:pt-28 lg:pb-24 lg:pt-32">
        <div class="grid items-center gap-12 lg:grid-cols-12 lg:gap-16">
            <div class="relative z-10 lg:col-span-7">
                <div class="mb-5 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-sky-400">
                    <span class="h-px w-7 bg-sky-500"></span>
                    Gobole Welding Shop · Bulan, Sorsogon
                </div>

                <h1 class="public-hero-title max-w-3xl text-4xl font-extrabold tracking-[-0.04em] text-white sm:text-6xl lg:text-[4.25rem] lg:leading-[1.02]">
                    Welding work built for the way you use it.
                </h1>

                <p class="public-hero-copy mt-6 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
                    Gates, repairs, fabrication, and on-site jobs. Request the work online, agree on the schedule, then follow the job without having to chase for updates.
                </p>

                <div class="mt-8 flex flex-col gap-3 sm:flex-row">
                    <RouterLink to="/signup" class="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-sky-600 px-6 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-500 active:scale-98">
                        Request a job
                        <ArrowRight class="h-4 w-4" />
                    </RouterLink>
                    <RouterLink to="/login" class="inline-flex h-11 items-center justify-center rounded-lg border border-slate-700 bg-slate-800/80 px-6 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-800 hover:text-white">
                        Check my booking
                    </RouterLink>
                </div>

                <div class="mt-8 flex flex-wrap gap-x-6 gap-y-2.5 border-t border-slate-800/60 pt-6">
                    <div v-for="point in trustPoints" :key="point" class="flex items-center gap-2 text-xs font-medium text-slate-400">
                        <Check class="h-4 w-4 text-sky-400" />
                        <span>{{ point }}</span>
                    </div>
                </div>
            </div>

            <div class="public-hero-visual relative mx-auto w-full max-w-lg lg:col-span-5 lg:mx-0 lg:max-w-none">
                <div class="relative overflow-hidden rounded-sm border border-slate-700/70 bg-slate-900 shadow-2xl">
                    <img src="https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?q=85&w=1400&auto=format&fit=crop" alt="Welder working on a steel fabrication" class="aspect-[4/5] w-full object-cover" />
                    <div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent"></div>
                    <div class="absolute inset-x-0 bottom-0 flex items-end justify-between gap-4 p-5 sm:p-6">
                        <div class="text-sm font-semibold text-white">Fabrication & repair</div>
                        <div class="flex items-center gap-1.5 text-xs text-slate-200"><MapPin class="h-3.5 w-3.5 text-sky-400" /> Bulan, Sorsogon</div>
                    </div>
                </div>
                <a href="tel:+639357705022" class="absolute -bottom-5 -left-4 inline-flex items-center gap-3 border border-slate-700 bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-xl transition hover:border-sky-500 sm:-left-7">
                    <Phone class="h-4 w-4 text-sky-400" />
                    <span><small class="block text-[10px] font-medium uppercase tracking-wider text-slate-400">Prefer to call?</small>+63 935 770 5022</span>
                </a>
            </div>
        </div>
    </section>
</template>

<style scoped>
</style>
