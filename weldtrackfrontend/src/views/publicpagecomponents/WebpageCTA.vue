<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next'
</script>

<template>
    <section class="relative py-16 sm:py-24 bg-public-bg border-t border-slate-800/60">
        <div class="relative mx-auto max-w-4xl px-6 text-center sm:px-10">
            <h2 data-reveal class="reveal text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Ready to start your project?
            </h2>
            <p data-reveal class="reveal mt-4 text-base leading-7 text-slate-300 max-w-2xl mx-auto">
                Create an account to book services, view transparent quotes, and track your welding projects from start to finish.
            </p>
            <div data-reveal class="reveal mt-8 flex items-center justify-center gap-4">
                <RouterLink to="/signup" class="group inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-sky-600 px-6 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-500 active:scale-98">
                    Create an Account
                    <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </RouterLink>
            </div>
        </div>
    </section>
</template>
