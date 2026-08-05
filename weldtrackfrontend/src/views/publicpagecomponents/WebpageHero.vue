<script setup lang="ts">
import {
    ArrowRight,
    CalendarDays,
    Check,
    CheckCircle2,
    Clock3,
    MapPin,
    ShieldCheck,
    Sparkles,
    Wrench,
} from 'lucide-vue-next'

const trustPoints = [
    'Verified email accounts',
    'Clear booking status',
    'One customer workspace',
]

const timeline = [
    { label: 'Request received', time: '8:42 AM', complete: true },
    { label: 'Schedule confirmed', time: '9:15 AM', complete: true },
    { label: 'Service in progress', time: 'Today', complete: false },
]
</script>

<template>
    <section id="home" class="public-hero relative mx-auto max-w-7xl px-6 pb-24 pt-16 sm:px-12 sm:pt-20 lg:pb-32 lg:pt-24">
        <div class="grid items-center gap-16 lg:grid-cols-[1.02fr_0.98fr] lg:gap-20">
            <div class="relative z-10 max-w-2xl">
                <div class="mb-7 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs font-bold tracking-[0.18em] text-cyan-300 uppercase">
                    <Sparkles class="h-3.5 w-3.5" />
                    Welding service, simplified
                </div>

                <h1 class="public-hero-title text-5xl font-black leading-[0.98] tracking-[-0.045em] text-white sm:text-6xl lg:text-[4.75rem]">
                    From service request to
                    <span class="relative mt-2 block w-fit bg-linear-to-r from-cyan-300 via-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        job done.
                        <span class="absolute -bottom-2 left-1 h-px w-3/4 bg-linear-to-r from-cyan-400/80 to-transparent"></span>
                    </span>
                </h1>

                <p class="public-hero-copy mt-9 max-w-xl text-lg leading-8 text-slate-300 sm:text-xl">
                    Book trusted welding services and follow every update from one clean customer portal—without repeated calls or paperwork.
                </p>

                <div class="mt-9 flex flex-col gap-4 sm:flex-row">
                    <RouterLink to="/signup" class="group inline-flex h-14 items-center justify-center gap-2 rounded-full bg-cyan-400 px-8 text-base font-extrabold text-slate-950 shadow-[0_18px_50px_rgba(34,211,238,0.2)] transition hover:-translate-y-0.5 hover:bg-cyan-300 hover:shadow-[0_22px_60px_rgba(34,211,238,0.3)] active:translate-y-0">
                        Book a service
                        <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </RouterLink>
                    <RouterLink to="/login" class="inline-flex h-14 items-center justify-center rounded-full border border-white/12 bg-white/5 px-8 text-base font-bold text-white backdrop-blur transition hover:border-white/20 hover:bg-white/10">
                        Track my booking
                    </RouterLink>
                </div>

                <div class="mt-9 flex flex-wrap gap-x-6 gap-y-3">
                    <div v-for="point in trustPoints" :key="point" class="flex items-center gap-2 text-sm font-medium text-slate-300">
                        <span class="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-400/10 text-emerald-300">
                            <Check class="h-3 w-3" :stroke-width="3" />
                        </span>
                        {{ point }}
                    </div>
                </div>
            </div>

            <div class="public-hero-visual relative mx-auto w-full max-w-[36rem] lg:mx-0">
                <div class="absolute -inset-12 rounded-full bg-cyan-400/10 blur-[90px]"></div>
                <div class="absolute -right-14 top-12 h-36 w-36 rounded-full border border-cyan-300/15"></div>
                <div class="absolute -right-6 top-20 h-20 w-20 rounded-full border border-cyan-300/10"></div>

                <div class="public-hero-panel relative overflow-hidden rounded-[2rem] border border-white/10 bg-slate-900/85 p-3 shadow-[0_40px_100px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-4">
                    <div class="overflow-hidden rounded-[1.35rem] border border-white/8 bg-public-hero">
                        <div class="flex items-center justify-between border-b border-white/8 px-5 py-4 sm:px-6">
                            <div class="flex items-center gap-3">
                                <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400 text-slate-950">
                                    <Wrench class="h-4 w-4" :stroke-width="2.5" />
                                </span>
                                <div>
                                    <div class="text-sm font-extrabold text-white">WeldTrack</div>
                                    <div class="text-[10px] font-bold tracking-[0.16em] text-slate-500 uppercase">Customer portal</div>
                                </div>
                            </div>
                            <span class="rounded-full border border-emerald-400/15 bg-emerald-400/10 px-3 py-1 text-[10px] font-extrabold tracking-wider text-emerald-300 uppercase">Active</span>
                        </div>

                        <div class="p-5 sm:p-6">
                            <div class="mb-5 flex items-end justify-between gap-4">
                                <div>
                                    <div class="text-xs font-bold tracking-[0.18em] text-cyan-300 uppercase">Current booking</div>
                                    <h2 class="mt-2 text-2xl font-black tracking-tight text-white">Steel gate repair</h2>
                                </div>
                                <span class="hidden rounded-xl bg-blue-400/10 p-2.5 text-blue-300 sm:flex">
                                    <ShieldCheck class="h-5 w-5" />
                                </span>
                            </div>

                            <div class="grid gap-3 sm:grid-cols-2">
                                <div class="rounded-2xl border border-white/8 bg-white/[0.035] p-4">
                                    <div class="flex items-center gap-2 text-xs font-semibold text-slate-500"><CalendarDays class="h-3.5 w-3.5" /> Schedule</div>
                                    <div class="mt-2 text-sm font-extrabold text-slate-100">August 7 · 9:00 AM</div>
                                </div>
                                <div class="rounded-2xl border border-white/8 bg-white/[0.035] p-4">
                                    <div class="flex items-center gap-2 text-xs font-semibold text-slate-500"><MapPin class="h-3.5 w-3.5" /> Service area</div>
                                    <div class="mt-2 text-sm font-extrabold text-slate-100">Bulan, Sorsogon</div>
                                </div>
                            </div>

                            <div class="mt-4 rounded-2xl border border-white/8 bg-white/[0.035] p-5">
                                <div class="mb-5 flex items-center justify-between">
                                    <span class="text-sm font-extrabold text-white">Booking progress</span>
                                    <span class="flex items-center gap-1.5 text-xs font-bold text-cyan-300"><Clock3 class="h-3.5 w-3.5" /> Updated now</span>
                                </div>
                                <div class="space-y-1">
                                    <div v-for="(item, index) in timeline" :key="item.label" class="relative flex gap-3 pb-5 last:pb-0">
                                        <span v-if="index < timeline.length - 1" :class="['absolute left-[9px] top-5 h-[calc(100%-4px)] w-px', item.complete ? 'bg-cyan-400/60' : 'bg-white/10']"></span>
                                        <span :class="['relative z-10 mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full', item.complete ? 'bg-cyan-400 text-slate-950' : 'border border-cyan-400 bg-cyan-400/10 text-cyan-300']">
                                            <Check v-if="item.complete" class="h-3 w-3" :stroke-width="3" />
                                            <span v-else class="h-1.5 w-1.5 rounded-full bg-cyan-300"></span>
                                        </span>
                                        <div class="flex min-w-0 flex-1 justify-between gap-3">
                                            <span :class="['text-sm font-bold', item.complete ? 'text-slate-200' : 'text-white']">{{ item.label }}</span>
                                            <span class="shrink-0 text-xs text-slate-500">{{ item.time }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="hero-float absolute -bottom-7 -left-3 flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-900/95 p-3.5 pr-5 shadow-2xl backdrop-blur-xl sm:-left-8">
                    <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-300"><CheckCircle2 class="h-5 w-5" /></span>
                    <div>
                        <div class="text-xs font-semibold text-slate-500">Next step</div>
                        <div class="text-sm font-extrabold text-white">We’ll keep you updated</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.hero-float { animation: heroFloat 5s ease-in-out infinite; }
@keyframes heroFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-7px); }
}
@media (prefers-reduced-motion: reduce) {
    .hero-float { animation: none; }
}
</style>
