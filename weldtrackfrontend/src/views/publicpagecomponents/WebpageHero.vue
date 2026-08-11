<script setup lang="ts">
import {
    ArrowRight,
    CalendarDays,
    Check,
    Clock3,
    MapPin,
    ShieldCheck,
    Wrench,
} from 'lucide-vue-next'

const trustPoints = [
    'Verified email accounts',
    'Clear booking status',
    'One customer workspace',
]

const proofPoints = [
    { value: '4 steps', label: 'From request to completion' },
    { value: '24/7', label: 'Booking status visibility' },
    { value: '1 portal', label: 'For every service update' },
]

const timeline = [
    { label: 'Request received', time: '8:42 AM', complete: true },
    { label: 'Schedule confirmed', time: '9:15 AM', complete: true },
    { label: 'Service in progress', time: 'Today', complete: false },
]
</script>

<template>
    <section id="home" class="public-hero relative mx-auto max-w-7xl px-6 pb-16 pt-24 sm:px-10 sm:pt-28 lg:pb-24 lg:pt-32">
        <div class="grid items-center gap-12 lg:grid-cols-12 lg:gap-12">
            <div class="relative z-10 lg:col-span-6">
                <div class="mb-5 inline-flex items-center gap-2 rounded-md border border-sky-500/30 bg-sky-500/10 px-3 py-1 text-xs font-semibold text-sky-400">
                    <ShieldCheck class="h-3.5 w-3.5" />
                    Commercial & Industrial Welding Operations
                </div>

                <h1 class="public-hero-title text-3xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-5xl lg:leading-[1.12]">
                    Professional welding services, managed end-to-end.
                </h1>

                <p class="public-hero-copy mt-5 max-w-xl text-base leading-7 text-slate-300 sm:text-lg">
                    Book precision welding services, view real-time job progress, and access project history from one structured customer portal.
                </p>

                <div class="mt-8 flex flex-col gap-3 sm:flex-row">
                    <RouterLink to="/signup" class="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-sky-600 px-6 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-500 active:scale-98">
                        Book a Service
                        <ArrowRight class="h-4 w-4" />
                    </RouterLink>
                    <RouterLink to="/login" class="inline-flex h-11 items-center justify-center rounded-lg border border-slate-700 bg-slate-800/80 px-6 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-800 hover:text-white">
                        Track Existing Booking
                    </RouterLink>
                </div>

                <div class="mt-8 flex flex-wrap gap-x-6 gap-y-2.5 border-t border-slate-800/60 pt-6">
                    <div v-for="point in trustPoints" :key="point" class="flex items-center gap-2 text-xs font-medium text-slate-400">
                        <Check class="h-4 w-4 text-sky-400" />
                        <span>{{ point }}</span>
                    </div>
                </div>
            </div>

            <div class="public-hero-visual relative mx-auto w-full max-w-lg lg:col-span-6 lg:mx-0 lg:max-w-none">
                <div class="public-hero-panel relative overflow-hidden rounded-xl border border-slate-800 bg-slate-900/90 shadow-2xl backdrop-blur-md">
                    <div class="flex items-center justify-between border-b border-slate-800 bg-slate-950/60 px-5 py-3.5">
                        <div class="flex items-center gap-2.5">
                            <span class="flex h-8 w-8 items-center justify-center rounded-md bg-sky-600 text-white">
                                <Wrench class="h-4 w-4" />
                            </span>
                            <div>
                                <div class="text-xs font-semibold text-white">WeldTrack Portal</div>
                                <div class="text-[11px] font-medium text-slate-400">Booking Console</div>
                            </div>
                        </div>
                        <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400">
                            <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                            Active Order
                        </span>
                    </div>

                    <div class="p-5 sm:p-6">
                        <div class="mb-5 flex items-start justify-between gap-4">
                            <div>
                                <div class="text-xs font-medium text-slate-400">Current Job</div>
                                <h2 class="mt-1 text-xl font-bold text-white sm:text-2xl">Structural Steel Gate Fabrication</h2>
                            </div>
                            <span class="rounded-md border border-slate-800 bg-slate-800/50 p-2 text-slate-400">
                                <Clock3 class="h-4 w-4" />
                            </span>
                        </div>

                        <div class="grid gap-3 sm:grid-cols-2">
                            <div class="rounded-lg border border-slate-800 bg-slate-950/50 p-3.5">
                                <div class="flex items-center gap-1.5 text-xs font-medium text-slate-400">
                                    <CalendarDays class="h-3.5 w-3.5 text-sky-400" />
                                    Schedule
                                </div>
                                <div class="mt-1 text-sm font-semibold text-slate-200">Aug 12 · 9:00 AM</div>
                            </div>
                            <div class="rounded-lg border border-slate-800 bg-slate-950/50 p-3.5">
                                <div class="flex items-center gap-1.5 text-xs font-medium text-slate-400">
                                    <MapPin class="h-3.5 w-3.5 text-sky-400" />
                                    Service Location
                                </div>
                                <div class="mt-1 text-sm font-semibold text-slate-200">Bulan, Sorsogon</div>
                            </div>
                        </div>

                        <div class="mt-4 rounded-lg border border-slate-800 bg-slate-950/50 p-4">
                            <div class="mb-4 flex items-center justify-between">
                                <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Status Timeline</span>
                                <span class="text-xs text-sky-400">Live Updates</span>
                            </div>
                            <div class="space-y-3">
                                <div v-for="(item, index) in timeline" :key="item.label" class="relative flex items-start gap-3">
                                    <span v-if="index < timeline.length - 1" :class="['absolute left-[9px] top-5 h-full w-px', item.complete ? 'bg-sky-500/50' : 'bg-slate-800']"></span>
                                    <span :class="['relative z-10 mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full', item.complete ? 'bg-sky-500 text-slate-950' : 'border border-slate-700 bg-slate-900 text-slate-400']">
                                        <Check v-if="item.complete" class="h-2.5 w-2.5" :stroke-width="3" />
                                        <span v-else class="h-1 w-1 rounded-full bg-slate-500"></span>
                                    </span>
                                    <div class="flex min-w-0 flex-1 justify-between gap-3 text-xs">
                                        <span :class="['font-medium', item.complete ? 'text-slate-200' : 'text-slate-400']">{{ item.label }}</span>
                                        <span class="text-slate-500">{{ item.time }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="public-proof-strip mt-16 grid divide-y divide-slate-800 rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm sm:grid-cols-3 sm:divide-x sm:divide-y-0 lg:mt-20">
            <div v-for="proof in proofPoints" :key="proof.label" class="px-6 py-5 text-center sm:text-left">
                <p class="text-xl font-bold tracking-tight text-white">{{ proof.value }}</p>
                <p class="mt-1 text-xs font-medium text-slate-400">{{ proof.label }}</p>
            </div>
        </div>
    </section>
</template>

<style scoped>
</style>
