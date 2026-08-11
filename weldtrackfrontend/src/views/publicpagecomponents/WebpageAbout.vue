<script setup lang="ts">
import { CalendarCheck2, LockKeyhole, MessagesSquare } from 'lucide-vue-next'

const highlights = [
    { icon: CalendarCheck2, number: '01', title: 'Simple booking flow', description: 'Choose a service and send a complete request from one guided workspace.' },
    { icon: MessagesSquare, number: '02', title: 'Updates without guesswork', description: 'See confirmations, schedules, and project progress without repeated calls.' },
    { icon: LockKeyhole, number: '03', title: 'A private customer portal', description: 'Keep addresses, requests, history, and feedback organized under your account.' },
]
</script>

<template>
    <section id="about" class="relative bg-public-dark py-16 sm:py-24 border-t border-slate-800/60">
        <div class="mx-auto max-w-7xl px-6 sm:px-10">
            <div class="grid gap-12 lg:grid-cols-12 lg:items-center lg:gap-16">
                <div data-reveal class="reveal relative order-2 lg:order-1 lg:col-span-5">
                    <div class="relative overflow-hidden rounded-xl border border-slate-800 bg-slate-900/80 p-2.5 shadow-xl">
                        <img src="https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1600&auto=format&fit=crop" alt="Welder completing a workshop project" class="aspect-[4/3] w-full rounded-lg object-cover sm:aspect-[16/10] lg:aspect-[4/5]" loading="lazy" />
                    </div>
                </div>

                <div class="order-1 lg:order-2 lg:col-span-7">
                    <p data-reveal class="reveal text-xs font-semibold uppercase tracking-wider text-sky-400">Why WeldTrack</p>
                    <h2 data-reveal class="reveal mt-3 max-w-2xl text-3xl font-bold tracking-tight text-white sm:text-4xl">Less chasing. More clarity.</h2>
                    <p data-reveal class="reveal mt-4 max-w-xl text-base leading-7 text-slate-300">A straightforward digital experience for customers who need dependable welding work and visibility at every stage.</p>

                    <div class="mt-8 space-y-3">
                        <article v-for="highlight in highlights" :key="highlight.title" data-reveal class="reveal flex gap-4 rounded-lg border border-slate-800 bg-slate-900/60 p-4 transition hover:border-slate-700 hover:bg-slate-900">
                            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-sky-500/10 text-sky-400"><component :is="highlight.icon" class="h-4 w-4" /></div>
                            <div class="min-w-0 flex-1"><div class="flex items-center justify-between gap-4"><h3 class="font-semibold text-white text-sm sm:text-base">{{ highlight.title }}</h3><span class="font-mono text-xs text-slate-500">{{ highlight.number }}</span></div><p class="mt-1 text-xs leading-5 text-slate-400">{{ highlight.description }}</p></div>
                        </article>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
