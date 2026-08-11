<script setup lang="ts">
import { ArrowUpRight } from 'lucide-vue-next'
</script>

<template>
    <footer class="border-t border-slate-800/60 bg-public-dark py-12">
        <div class="mx-auto max-w-7xl px-6 sm:px-10">
            <div class="grid gap-8 border-b border-slate-800/60 pb-8 md:grid-cols-[1.3fr_0.7fr_0.8fr]">
                <div class="max-w-md">
                    <RouterLink to="/" class="inline-flex items-center" aria-label="WeldTrack home"><img src="/weldtrack.png" alt="WeldTrack Logo" class="h-9 w-auto object-contain" /></RouterLink>
                    <p class="mt-4 text-xs leading-6 text-slate-400">A structured platform to request welding services and track project progress end-to-end.</p>
                </div>
                <div><p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Navigation</p><nav class="mt-3 flex flex-col gap-2 text-xs text-slate-300"><RouterLink to="/#about" class="hover:text-white">Why WeldTrack</RouterLink><RouterLink to="/#services" class="hover:text-white">Services</RouterLink><RouterLink to="/#contact" class="hover:text-white">Contact Support</RouterLink></nav></div>
                <div><p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Account</p><div class="mt-3 flex flex-col gap-2 text-xs text-slate-300"><RouterLink to="/login" class="inline-flex items-center gap-1 hover:text-white">Sign In <ArrowUpRight class="h-3 w-3" /></RouterLink><RouterLink to="/signup" class="inline-flex items-center gap-1 hover:text-white">Create Account <ArrowUpRight class="h-3 w-3" /></RouterLink></div></div>
            </div>
            <div class="flex flex-col gap-4 pt-6 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between"><p>&copy; 2026 WeldTrack Management Systems.</p><div class="flex gap-4"><RouterLink to="/privacy" class="hover:text-slate-300">Privacy Policy</RouterLink><RouterLink to="/terms" class="hover:text-slate-300">Terms of Service</RouterLink></div></div>
        </div>
    </footer>
</template>
