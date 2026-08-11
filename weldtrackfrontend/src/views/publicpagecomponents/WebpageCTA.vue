<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next'
</script>

<template>
    <section class="relative py-16 sm:py-24 bg-public-bg overflow-hidden border-t border-slate-200/5 dark:border-white/5">
        <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[400px] w-[600px] rounded-full bg-cyan-500/10 blur-[100px]"></div>
        
        <div class="relative mx-auto max-w-4xl px-6 text-center sm:px-12">
            <h2 data-reveal class="reveal text-3xl font-bold tracking-tight text-[color:var(--public-text)] sm:text-5xl">
                Ready to start your project?
            </h2>
            <p data-reveal class="reveal mt-6 text-lg leading-8 text-slate-500 max-w-2xl mx-auto">
                Join our platform today to book services, track progress, and manage all your welding projects from one easy-to-use dashboard.
            </p>
            <div data-reveal class="reveal mt-10 flex items-center justify-center gap-4">
                <RouterLink to="/signup" class="group inline-flex h-14 items-center justify-center gap-2 rounded-xl bg-[color:var(--public-text)] px-8 text-base font-extrabold text-[color:var(--public-bg)] shadow-xl transition hover:-translate-y-0.5 hover:opacity-90 hover:shadow-2xl active:translate-y-0">
                    Create an account
                    <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </RouterLink>
            </div>
        </div>
    </section>
</template>
