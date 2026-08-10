<script setup lang="ts">
import { CalendarCheck2, LockKeyhole, MessagesSquare } from 'lucide-vue-next'

const highlights = [
    { icon: CalendarCheck2, number: '01', title: 'Simple booking flow', description: 'Choose a service and send a complete request from one guided workspace.' },
    { icon: MessagesSquare, number: '02', title: 'Updates without guesswork', description: 'See confirmations, schedules, and project progress without repeated calls.' },
    { icon: LockKeyhole, number: '03', title: 'A private customer portal', description: 'Keep addresses, requests, history, and feedback organized under your account.' },
]
</script>

<template>
    <section id="about" class="relative bg-public-dark py-24 sm:py-32">
        <div class="mx-auto max-w-7xl px-6 sm:px-12">
            <div class="grid gap-14 lg:grid-cols-[0.92fr_1.08fr] lg:items-center lg:gap-20">
                <div data-reveal class="reveal relative order-2 lg:order-1">
                    <div class="absolute -inset-8 rounded-full bg-cyan-500/10 blur-[100px]"></div>
                    <div class="relative overflow-hidden rounded-[2rem] border border-white/10 bg-public-panel p-3 shadow-2xl">
                        <img src="https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1600&auto=format&fit=crop" alt="Welder completing a workshop project" class="aspect-[4/5] w-full rounded-[1.35rem] object-cover sm:aspect-[5/4] lg:aspect-[4/5]" loading="lazy" />
                        <div class="public-about-overlay absolute inset-x-7 bottom-7 rounded-2xl border border-white/10 bg-slate-950/75 p-5 text-white shadow-xl backdrop-blur-xl">
                            <p class="text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">Designed around your booking</p>
                            <p class="mt-2 text-lg font-bold">Clear progress from first request to finished work.</p>
                        </div>
                    </div>
                </div>

                <div class="order-1 lg:order-2">
                    <p data-reveal class="reveal text-sm font-bold uppercase tracking-[0.3em] text-cyan-500">Why WeldTrack</p>
                    <h2 data-reveal class="reveal mt-4 max-w-2xl text-4xl font-black tracking-[-0.035em] text-white sm:text-5xl">Less chasing. More clarity.</h2>
                    <p data-reveal class="reveal mt-6 max-w-xl text-lg leading-8 text-slate-400">A straightforward digital experience for customers who need dependable welding work and visibility at every stage.</p>

                    <div class="mt-10 space-y-3">
                        <article v-for="highlight in highlights" :key="highlight.title" data-reveal class="reveal group flex gap-4 rounded-2xl border border-white/8 bg-white/[0.025] p-5 transition hover:border-cyan-400/20 hover:bg-white/[0.05]">
                            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300 ring-1 ring-cyan-400/15"><component :is="highlight.icon" class="h-5 w-5" /></div>
                            <div class="min-w-0 flex-1"><div class="flex items-center justify-between gap-4"><h3 class="font-bold text-white sm:text-lg">{{ highlight.title }}</h3><span class="font-mono text-xs text-slate-600">{{ highlight.number }}</span></div><p class="mt-1.5 leading-6 text-slate-400">{{ highlight.description }}</p></div>
                        </article>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
