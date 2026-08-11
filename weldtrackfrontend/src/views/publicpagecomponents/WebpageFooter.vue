<script setup lang="ts">
import { ArrowUpRight } from 'lucide-vue-next'
</script>

<template>
    <footer class="border-t border-white/5 bg-public-dark py-16">
        <div class="mx-auto max-w-7xl px-6 sm:px-12">
            <div class="grid gap-10 border-b border-white/8 pb-10 md:grid-cols-[1.3fr_0.7fr_0.8fr]">
                <div class="max-w-md">
                    <RouterLink to="/" class="inline-flex items-center" aria-label="WeldTrack home"><img src="/weldtrack.png" alt="WeldTrack Logo" class="h-16 w-auto object-contain" /></RouterLink>
                    <p class="mt-5 text-sm leading-7 text-slate-500">A simpler way to request welding services and follow every important project update.</p>
                </div>
                <div><p class="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">Explore</p><nav class="mt-4 flex flex-col gap-3 text-sm text-slate-400"><RouterLink to="/#about" class="hover:text-[color:var(--public-text)]">Why WeldTrack</RouterLink><RouterLink to="/#services" class="hover:text-[color:var(--public-text)]">Services</RouterLink><RouterLink to="/#contact" class="hover:text-[color:var(--public-text)]">Contact</RouterLink></nav></div>
                <div><p class="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">Customer portal</p><div class="mt-4 flex flex-col gap-3 text-sm text-slate-400"><RouterLink to="/login" class="inline-flex items-center gap-1 hover:text-[color:var(--public-text)]">Sign in <ArrowUpRight class="h-3.5 w-3.5" /></RouterLink><RouterLink to="/signup" class="inline-flex items-center gap-1 hover:text-[color:var(--public-text)]">Create account <ArrowUpRight class="h-3.5 w-3.5" /></RouterLink></div></div>
            </div>
            <div class="flex flex-col gap-4 pt-8 text-xs text-slate-600 sm:flex-row sm:items-center sm:justify-between"><p>&copy; 2026 WeldTrack Management Systems.</p><div class="flex gap-5"><RouterLink to="/privacy" class="hover:text-slate-400">Privacy</RouterLink><RouterLink to="/terms" class="hover:text-slate-400">Terms</RouterLink></div></div>
        </div>
    </footer>
</template>
